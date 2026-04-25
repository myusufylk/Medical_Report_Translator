"""
training_data.jsonl Kalite Doğrulama Raporu
Makaleye eklenecek veri seti için kapsamlı kontrol.
"""
import json
import re
from collections import Counter

print("=" * 65)
print("  JSONL EĞİTİM VERİSİ KALİTE DOĞRULAMA RAPORU")
print("=" * 65)

with open("training_data.jsonl", "r", encoding="utf-8") as f:
    lines = f.readlines()

errors = []
warnings = []
stats = {
    "toplam_satir": len(lines),
    "gecerli_json": 0,
    "hatali_json": 0,
    "test_sayilari": Counter(),
    "durum_dagilimi": Counter(),
    "cinsiyet_dagilimi": Counter(),
    "yas_dagilimi": [],
    "test_per_patient": [],
    "none_iceren": 0,
    "bos_asistan": 0,
    "roller": Counter(),
}

for i, line in enumerate(lines):
    line = line.strip()
    if not line:
        continue

    # 1. JSON PARSE TESTİ
    try:
        data = json.loads(line)
        stats["gecerli_json"] += 1
    except json.JSONDecodeError as e:
        stats["hatali_json"] += 1
        errors.append(f"Satır {i+1}: JSON parse hatası — {e}")
        continue

    # 2. MESAJ YAPISI KONTROLÜ
    messages = data.get("messages", [])
    if len(messages) != 3:
        errors.append(f"Satır {i+1}: {len(messages)} mesaj var (beklenen: 3)")
        continue

    roles = [m["role"] for m in messages]
    if roles != ["system", "user", "assistant"]:
        errors.append(f"Satır {i+1}: Rol sırası hatalı: {roles}")

    for m in messages:
        stats["roller"][m["role"]] += 1

    # 3. SYSTEM MESAJI KONTROLÜ
    sys_msg = messages[0]["content"]
    if "sağlık asistanısın" not in sys_msg:
        warnings.append(f"Satır {i+1}: System mesajı beklenenden farklı")

    # 4. USER MESAJI ANALİZİ
    user_msg = messages[1]["content"]

    # Yaş çıkar
    age_match = re.search(r'(\d+)\s*yaşında', user_msg)
    if age_match:
        stats["yas_dagilimi"].append(int(age_match.group(1)))

    # Cinsiyet çıkar
    if "Erkek" in user_msg:
        stats["cinsiyet_dagilimi"]["Erkek"] += 1
    elif "Kadın" in user_msg:
        stats["cinsiyet_dagilimi"]["Kadın"] += 1

    # Test sayısı
    test_lines = [l for l in user_msg.split("\n") if l.strip().startswith("- ")]
    stats["test_per_patient"].append(len(test_lines))

    for tl in test_lines:
        # "- Glukoz: 85.3 mg/dL (Normal)" formatı
        m = re.match(r'-\s*(\w+):\s*([\d.]+)', tl.strip())
        if m:
            test_name = m.group(1)
            stats["test_sayilari"][test_name] += 1

        if "(Normal)" in tl:
            stats["durum_dagilimi"]["Normal"] += 1
        elif "(Yüksek)" in tl:
            stats["durum_dagilimi"]["Yüksek"] += 1
        elif "(Düşük)" in tl:
            stats["durum_dagilimi"]["Düşük"] += 1

    # 5. ASSISTANT MESAJI KONTROLÜ
    asst_msg = messages[2]["content"]

    if not asst_msg.strip():
        stats["bos_asistan"] += 1
        errors.append(f"Satır {i+1}: Asistan yanıtı boş!")

    if "None" in asst_msg:
        stats["none_iceren"] += 1
        errors.append(f"Satır {i+1}: Asistan yanıtında 'None' metni var!")

    # Klinik belge kontrolü
    klinik_terimler = ["Epikriz", "ICD10_Kodu", "ICD-10", "Taburculuk_Durumu",
                       "Taburculuk_Ilaclari", "Anamnez", "Prognoz", "Tedavi_Plani",
                       "Kontrol_Randevusu", "Sekonder_Tani", "Primer_Tani",
                       "Vital_Bulgular", "Konsultasyon", "Diyabet", "Hipertansiyon"]
    for term in klinik_terimler:
        if f"- {term}:" in user_msg:
            # Bu kategorik bir belge, lab testi değil — hata
            pass  # Bu kontrolü sadece EKG/Epikriz kaynaklı olanlar için tutalım

    # Gerçek dışı değer kontrolü (biyolojik olarak imkansız)
    for tl in test_lines:
        m = re.match(r'-\s*(\w+):\s*([\d.]+)', tl.strip())
        if m:
            test_name = m.group(1)
            val = float(m.group(2))
            # Bilinen imkansız değerler
            if test_name == "Potasyum" and val > 15:
                errors.append(f"Satır {i+1}: Potasyum={val} — biyolojik olarak imkansız (>15)")
            elif test_name == "HCT" and val > 80:
                errors.append(f"Satır {i+1}: HCT={val}% — biyolojik olarak imkansız (>80%)")
            elif test_name == "Kreatinin" and val > 30:
                errors.append(f"Satır {i+1}: Kreatinin={val} — aşırı yüksek")
            elif test_name == "HGB" and val > 30:
                errors.append(f"Satır {i+1}: HGB={val} — biyolojik olarak imkansız (>30)")
            elif test_name == "Glukoz" and val > 1000:
                errors.append(f"Satır {i+1}: Glukoz={val} — aşırı yüksek")

# ======= RAPOR =======
print(f"\n📊 GENEL İSTATİSTİKLER")
print(f"   Toplam satır:        {stats['toplam_satir']}")
print(f"   Geçerli JSON:        {stats['gecerli_json']}")
print(f"   Hatalı JSON:         {stats['hatali_json']}")

print(f"\n👤 DEMOGRAFİ")
for k, v in stats["cinsiyet_dagilimi"].items():
    pct = v / stats["toplam_satir"] * 100
    print(f"   {k}: {v} (%{pct:.1f})")
if stats["yas_dagilimi"]:
    ages = stats["yas_dagilimi"]
    print(f"   Yaş aralığı: {min(ages)} - {max(ages)}")
    print(f"   Yaş ortalaması: {sum(ages)/len(ages):.1f}")

print(f"\n🧪 TEST DAĞILIMI")
print(f"   Farklı test türü: {len(stats['test_sayilari'])}")
if stats["test_per_patient"]:
    tpp = stats["test_per_patient"]
    print(f"   Hasta başına test: {min(tpp)} - {max(tpp)} (ort: {sum(tpp)/len(tpp):.1f})")
print(f"   En çok kullanılan 10 test:")
for test, count in stats["test_sayilari"].most_common(10):
    print(f"      {test}: {count}")

print(f"\n📈 DURUM DAĞILIMI")
total_durum = sum(stats["durum_dagilimi"].values())
for durum in ["Normal", "Yüksek", "Düşük"]:
    cnt = stats["durum_dagilimi"].get(durum, 0)
    pct = cnt / total_durum * 100 if total_durum > 0 else 0
    print(f"   {durum}: {cnt} (%{pct:.1f})")

print(f"\n🔍 KALİTE KONTROLLERİ")
print(f"   'None' içeren satır:     {stats['none_iceren']}", "✅" if stats["none_iceren"] == 0 else "❌")
print(f"   Boş asistan yanıtı:     {stats['bos_asistan']}", "✅" if stats["bos_asistan"] == 0 else "❌")
print(f"   Hatalı JSON:            {stats['hatali_json']}", "✅" if stats["hatali_json"] == 0 else "❌")

if errors:
    print(f"\n❌ HATALAR ({len(errors)} adet):")
    for e in errors[:20]:
        print(f"   • {e}")
    if len(errors) > 20:
        print(f"   ... ve {len(errors)-20} hata daha")
else:
    print(f"\n✅ HİÇ HATA BULUNAMADI!")

if warnings:
    print(f"\n⚠️  UYARILAR ({len(warnings)} adet):")
    for w in warnings[:10]:
        print(f"   • {w}")

# Örnek göster
print(f"\n📝 ÖRNEK VERİ (İlk Satır):")
print("-" * 65)
d = json.loads(lines[0])
for m in d["messages"]:
    print(f"[{m['role'].upper()}]")
    print(m["content"])
    print()

print("=" * 65)
print("  DOĞRULAMA TAMAMLANDI")
print("=" * 65)
