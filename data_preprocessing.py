import pandas as pd
import json
import random
import os
import re
import numpy as np

# ================================================================
# BÖLÜM 1: JSON SÖZLÜKLERDEN REFERANS ARALIKLERINI OKU VE PARSE ET
# ================================================================

def parse_normal_aralik(text, gender="Erkek"):
    """
    normal_aralik metnini parse ederek (low, high) tuple döndürür.
    Cinsiyet bazlı aralıklar için gender parametresi kullanılır.
    Dönen değer: (normal_min, normal_max) ya da None
    """
    if not text:
        return None

    # Türkçe sayı formatını normalize et: "0,7" → "0.7", "4.000" → "4000"
    def normalize(s):
        s = s.strip()
        # Binlik ayraç olarak nokta kullanımı: "4.000" → "4000"
        s = re.sub(r'(\d)\.(\d{3})', r'\1\2', s)
        # Ondalık virgül: "0,7" → "0.7"
        s = s.replace(',', '.')
        return s

    # Em dash ve normal tire → standart tire
    text = text.replace('–', '-').replace('—', '-')

    # Cinsiyete göre bölme: "Erkek: X-Y; Kadın: A-B"
    if 'Erkek:' in text and 'Kadın:' in text:
        if gender == "Erkek":
            match = re.search(r'Erkek:\s*([\d.,]+)\s*-\s*([\d.,]+)', text)
        else:
            match = re.search(r'Kadın:\s*([\d.,]+)\s*-\s*([\d.,]+)', text)
        if match:
            lo = float(normalize(match.group(1)))
            hi = float(normalize(match.group(2)))
            return (lo, hi)

    # "X – Y /µL veya %A – %B" formatı: mutlak sayıyı kullan (ilk kısım)
    # Örn: "2.000 – 7.000 /µL veya %40 – %70" → (2000, 7000)
    if 'veya' in text:
        ilk_kisim = text.split('veya')[0]
        std_first = re.search(r'([\d.,]+)\s*-\s*([\d.,]+)', ilk_kisim)
        if std_first:
            return (float(normalize(std_first.group(1))), float(normalize(std_first.group(2))))

    # Yüzde işareti olan (tek aralık): "%11,5 - %14,5", "%40 - %54"
    # Sadece "veya" olmayan, saf yüzde aralıkları için (RDW, HCT gibi)
    pct = re.search(r'%\s*([\d.,]+)\s*-\s*%?\s*([\d.,]+)', text)
    if pct:
        return (float(normalize(pct.group(1))), float(normalize(pct.group(2))))

    # Standart aralık: "70 - 100" ya da "0.7 - 1.3"
    std = re.search(r'([\d.,]+)\s*-\s*([\d.,]+)', text)
    if std:
        return (float(normalize(std.group(1))), float(normalize(std.group(2))))

    # "< X" formatı (sadece üst sınır, örn. HbA1c normal < 5.7)
    lt = re.search(r'<\s*%?\s*([\d.,]+)', text.split(';')[0])
    if lt:
        val = float(normalize(lt.group(1)))
        return (0.0, val)

    return None


def load_dictionaries():
    """Tüm JSON sözlüklerini yükler ve referans aralıklarını parse eder.
    
    Önemli: Sadece biyokimya ve hemogram testleri sayısal veri üretiminde kullanılır.
    EKG ve epikriz dosyaları sözlük açıklamaları için yüklenir ama
    bunlar klinik bulgu/belge olduğundan sayısal test olarak dahil edilmez.
    """
    sozluk = {}
    referans = {}

    # Tüm sözlük dosyaları (açıklama için)
    all_files = ['biyokimya.json', 'hemogram.json', 'ekg.json', 'epikriz.json']
    # Sadece gerçek lab testleri (sayısal veri üretimi için)
    lab_files = ['biyokimya.json', 'hemogram.json']

    for fname in all_files:
        if not os.path.exists(fname):
            continue
        with open(fname, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for test_adi, info in data.items():
                    sozluk[test_adi] = info

                    # Sadece lab dosyalarından sayısal referans parse et
                    if fname in lab_files:
                        aralik_text = info.get('normal_aralik', '')
                        ref_e = parse_normal_aralik(aralik_text, gender="Erkek")
                        ref_k = parse_normal_aralik(aralik_text, gender="Kadın")

                        if ref_e or ref_k:
                            referans[test_adi] = {
                                "E": ref_e or ref_k,
                                "K": ref_k or ref_e,
                                "aralik_text": aralik_text
                            }
            except Exception as e:
                print(f"⚠️  {fname} okunamadı: {e}")

    return sozluk, referans


def generate_value(normal_range, durum):
    """Normal aralığa göre Düşük/Normal/Yüksek değer üret."""
    lo, hi = normal_range
    span = hi - lo

    if durum == "Normal":
        return round(random.uniform(lo, hi), 2)
    elif durum == "Düşük":
        # Normal aralığın altında: lo'nun %20-%80'i kadar düşük
        low_min = max(0, lo - span * 0.8)
        low_max = max(0, lo - span * 0.05)
        if low_min >= low_max:
            low_min = max(0, lo * 0.3)
            low_max = max(0, lo * 0.9)
        return round(random.uniform(low_min, low_max), 2)
    else:  # Yüksek
        high_min = hi + span * 0.05
        high_max = hi + span * 1.5
        return round(random.uniform(high_min, high_max), 2)


def generate_synthetic_data(sozluk, referans, num_patients=1200):
    """
    Yalnızca gerçek lab testleri olan testler için veri üret.
    Epikriz, ICD10, klinik belge türlerini hariç tut.
    """
    # Sadece parse edilebilen numeric testleri kullan
    numeric_tests = list(referans.keys())
    print(f"      → Sayısal parse edilebilen {len(numeric_tests)} test: {numeric_tests[:5]}...")

    ages = list(range(18, 91))
    weights = [3 if 40 <= a <= 75 else (1.5 if 30 <= a < 40 or 75 < a <= 85 else 1) for a in ages]
    total_w = sum(weights)
    age_probs = [w / total_w for w in weights]

    demographics, labs = [], []

    for i in range(1, num_patients + 1):
        patient_id = f"P{i:05d}"
        age    = int(np.random.choice(ages, p=age_probs))
        gender = random.choice(["Erkek", "Kadın"])
        demographics.append({"patient_id": patient_id, "age": age, "gender": gender})

        num_tests = random.randint(2, 5)
        selected  = random.sample(numeric_tests, min(num_tests, len(numeric_tests)))

        for test in selected:
            ref     = referans[test]
            ck      = "E" if gender == "Erkek" else "K"
            normal_range = ref[ck]

            # %60 Normal, %25 Yüksek, %15 Düşük
            durum = random.choices(["Normal", "Yüksek", "Düşük"], weights=[60, 25, 15])[0]
            val   = generate_value(normal_range, durum)

            # Üretilen değere göre gerçek durumu hesapla
            lo, hi = normal_range
            if val < lo:
                gercek_durum = "Düşük"
            elif val > hi:
                gercek_durum = "Yüksek"
            else:
                gercek_durum = "Normal"

            # Birim bilgisini normal_aralik metninden çıkar
            aralik = ref.get("aralik_text", "")
            birim_match = re.search(r'(mg/dL|g/dL|U/L|mIU/L|mEq/L|mmol/L|fL|pg|%|/µL|milyon/µL|IU/L|ms)', aralik)
            birim = birim_match.group(1) if birim_match else ""

            labs.append({
                "patient_id": patient_id,
                "test_name":  test,
                "test_value": val,
                "birim":      birim,
                "durum":      gercek_durum
            })

    pd.DataFrame(demographics).to_csv("demographic.csv", index=False, encoding="utf-8")
    pd.DataFrame(labs).to_csv("labs.csv", index=False, encoding="utf-8")
    print(f"✅ {num_patients} hastalık 'labs.csv' ve 'demographic.csv' oluşturuldu.")


def generate_jsonl(sozluk):
    """lab verilerini ve sözlük açıklamalarını birleştirip JSONL üret."""
    if not os.path.exists("demographic.csv") or not os.path.exists("labs.csv"):
        print("❌ CSV dosyaları bulunamadı.")
        return

    df_merged = pd.merge(
        pd.read_csv("demographic.csv"),
        pd.read_csv("labs.csv"),
        on="patient_id"
    )

    jsonl_data = []

    for patient_id, group in df_merged.groupby("patient_id"):
        age    = group["age"].iloc[0]
        gender = group["gender"].iloc[0]

        user_lines      = [f"Hasta Bilgileri: {age} yaşında, {gender}.", "Laboratuvar Sonuçları:"]
        assistant_lines = ["Laboratuvar sonuçlarının değerlendirmesi:", ""]

        for _, row in group.iterrows():
            test  = row["test_name"]
            durum = row["durum"]
            val   = row["test_value"]
            birim_raw = row.get("birim", "")
            # NaN kontrolü (pandas boş hücreleri NaN yapar)
            birim = str(birim_raw).strip() if pd.notna(birim_raw) and str(birim_raw).strip().lower() != "nan" else ""

            # Büyük sayılar için okunabilir format (PLT, WBC gibi)
            if val >= 1000:
                val_str = f"{int(val):,}".replace(",", ".")
            else:
                val_str = str(val)

            birim_str = f" {birim}" if birim else ""
            user_lines.append(f"- {test}: {val_str}{birim_str} ({durum})")

            if test in sozluk:
                info     = sozluk[test]
                tam_adi  = info.get("tam_adi") or test
                sade     = (info.get("sade_aciklama") or "").strip()
                normal_r = (info.get("normal_aralik") or "").strip()

                if durum == "Düşük":
                    yorum = info.get("dusukse") or ""
                elif durum == "Yüksek":
                    yorum = info.get("yuksekse") or ""
                else:
                    yorum = f"Değer normal referans aralığında ({normal_r}) yer almaktadır."

                # None veya boş yorum kontrolü
                if not yorum or yorum.strip().lower() == "none":
                    yorum = "Bu değer için doktorunuza başvurmanız önerilir."

                line = f"**{tam_adi}**: {sade} {yorum}".strip()
            else:
                if durum == "Normal":
                    line = f"**{test}**: Değer normal referans aralığındadır."
                elif durum == "Düşük":
                    line = f"**{test}**: Değer referans aralığının altındadır. Lütfen doktorunuza danışın."
                else:
                    line = f"**{test}**: Değer referans aralığının üstündedir. Lütfen doktorunuza danışın."

            assistant_lines.append(line)

        jsonl_data.append({
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Sen tıbbi tahlilleri hastaların anlayabileceği sade ve anlaşılır bir dille "
                        "açıklayan uzman bir sağlık asistanısın. Asla kesin bir tanı koymazsın, "
                        "sadece değerleri yorumlarsın ve gerektiğinde doktora başvurulmasını önerirsin."
                    )
                },
                {"role": "user",      "content": "\n".join(user_lines).strip()},
                {"role": "assistant", "content": "\n".join(assistant_lines).strip()}
            ]
        })

    with open("training_data.jsonl", "w", encoding="utf-8") as f:
        for item in jsonl_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"✅ Toplam {len(jsonl_data)} satırlık JSONL eğitim verisi 'training_data.jsonl' dosyasına kaydedildi.")


if __name__ == "__main__":
    print("=" * 55)
    print("  Tıbbi Eğitim Verisi Ön İşleme")
    print("  (Referans aralıkları doğrudan JSON sözlüklerinden)")
    print("=" * 55)

    print("\n[1/3] Tahlil sözlükleri yükleniyor ve parse ediliyor...")
    sozluk, referans = load_dictionaries()
    print(f"      → {len(sozluk)} tahlil tanımı, {len(referans)} numeric test")

    print("\n[2/3] Gerçekçi hasta verisi üretiliyor...")
    generate_synthetic_data(sozluk, referans, num_patients=1200)

    print("\n[3/3] JSONL eğitim verisi oluşturuluyor...")
    generate_jsonl(sozluk)

    print("\n" + "=" * 55)
    print("  İşlem başarıyla tamamlandı!")
    print("=" * 55)
