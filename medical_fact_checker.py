"""
medical_fact_checker.py
========================
Tıbbi Doğruluk Kontrolü (Fact-Check) Algoritması

AI'ın ürettiği tıbbi yorumları, mevcut JSON sözlüklerine karşı doğrulayan
kural tabanlı bir doğrulama motoru. AI halüsinasyonlarını, çelişkileri ve
tıbbi hataları otomatik tespit eder.

Kontrol Katmanları:
  1. Değer-Durum Uyumu     → Sayısal değer ile belirtilen durum eşleşiyor mu?
  2. Birim Doğruluğu       → Test için doğru birim kullanılmış mı?
  3. Kritik Değer Tespiti   → Tehlikeli eşikler aşılmışsa uyarı var mı?
  4. Cinsiyet Tutarlılığı   → Cinsiyete özel aralıklar doğru kullanılmış mı?
  5. Açıklama Tutarlılığı   → Durum ile açıklama çelişiyor mu?
  6. Halüsinasyon Tespiti   → Sözlükte olmayan test/terim uydurulmuş mu?

Kullanım:
  checker = MedicalFactChecker()
  rapor = checker.check_ai_response(ai_yanit_metni)
  rapor.yazdir()
"""

import json
import re
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ================================================================
# BÖLÜM 1: SABITLER VE VERİ YAPILARI
# ================================================================

class Severity(Enum):
    """Bulgu ciddiyet seviyeleri."""
    ERROR   = "❌ HATA"
    WARNING = "⚠️  UYARI"
    INFO    = "ℹ️  BİLGİ"


@dataclass
class Finding:
    """Tek bir doğrulama bulgusu."""
    severity: Severity
    category: str        # Kontrol katmanı adı
    test_name: str       # İlgili test
    message: str         # Açıklama
    suggestion: str = "" # Düzeltme önerisi


@dataclass
class FactCheckReport:
    """Doğrulama raporu."""
    findings: list = field(default_factory=list)
    checks_passed: int = 0
    checks_total: int = 0

    @property
    def errors(self):
        return [f for f in self.findings if f.severity == Severity.ERROR]

    @property
    def warnings(self):
        return [f for f in self.findings if f.severity == Severity.WARNING]

    @property
    def infos(self):
        return [f for f in self.findings if f.severity == Severity.INFO]

    @property
    def score(self):
        """0-100 arası güvenilirlik skoru (oransal hesaplama).
        
        Hata oranı ve uyarı oranı toplam kontrol sayısına göre hesaplanır.
        Hata ağırlığı: 3x, Uyarı ağırlığı: 0.5x
        """
        if self.checks_total == 0:
            return 100
        error_rate = len(self.errors) / self.checks_total
        warning_rate = len(self.warnings) / self.checks_total
        raw = 100 * (1 - error_rate * 3 - warning_rate * 0.5)
        return max(0, min(100, round(raw, 1)))

    def yazdir(self):
        """Raporu konsola yazdır."""
        print("=" * 65)
        print("  TIBBI DOĞRULUK KONTROLÜ RAPORU")
        print("=" * 65)

        print(f"\n📊 ÖZET")
        print(f"   Toplam kontrol:  {self.checks_total}")
        print(f"   Başarılı:        {self.checks_passed}")
        print(f"   Hata:            {len(self.errors)}")
        print(f"   Uyarı:           {len(self.warnings)}")
        print(f"   Bilgi:           {len(self.infos)}")
        print(f"   Güvenilirlik:    %{self.score}")

        if self.errors:
            print(f"\n{Severity.ERROR.value} ({len(self.errors)} adet):")
            for f in self.errors:
                print(f"   [{f.category}] {f.test_name}: {f.message}")
                if f.suggestion:
                    print(f"      → Öneri: {f.suggestion}")

        if self.warnings:
            print(f"\n{Severity.WARNING.value} ({len(self.warnings)} adet):")
            for f in self.warnings:
                print(f"   [{f.category}] {f.test_name}: {f.message}")
                if f.suggestion:
                    print(f"      → Öneri: {f.suggestion}")

        if self.infos:
            print(f"\n{Severity.INFO.value} ({len(self.infos)} adet):")
            for f in self.infos[:5]:  # En fazla 5 bilgi göster
                print(f"   [{f.category}] {f.test_name}: {f.message}")
            if len(self.infos) > 5:
                print(f"   ... ve {len(self.infos) - 5} bilgi daha")

        if not self.findings:
            print(f"\n✅ TÜM KONTROLLER BAŞARILI!")

        print("\n" + "=" * 65)


# ================================================================
# BÖLÜM 2: REFERANS ARALIKLARINI PARSE ETME
# ================================================================

def _normalize_number(s):
    """Türkçe sayı formatını float'a çevir."""
    s = s.strip()
    s = re.sub(r'(\d)\.(\d{3})', r'\1\2', s)  # Binlik: 4.000 → 4000
    s = s.replace(',', '.')  # Ondalık: 0,7 → 0.7
    return float(s)


def parse_tehlikeli_deger(text):
    """tehlikeli_deger metninden eşik değerlerini çıkar.
    
    Döndürür: list of (operator, value, description)
    Örn: "< 40 mg/dL (bilinç kaybı)" → [('<', 40.0, 'bilinç kaybı riski')]
    """
    if not text:
        return []

    results = []
    # "< X" veya "> X" formatlarını bul
    text = text.replace('–', '-').replace('—', '-')
    patterns = re.findall(
        r'([<>≥≤])\s*%?\s*([\d.,]+)\s*(?:mg/dL|g/dL|U/L|mIU/L|mEq/L|mmol/L|fL|pg|%|/µL|/dk|mmHg|°C)?\s*\(([^)]+)\)',
        text
    )
    for op, val, desc in patterns:
        try:
            v = _normalize_number(val)
            results.append((op, v, desc.strip()))
        except ValueError:
            pass

    return results


def parse_range(text, gender="Erkek"):
    """normal_aralik metninden (min, max) aralığını parse et."""
    if not text:
        return None

    text = text.replace('–', '-').replace('—', '-')

    # Cinsiyete göre
    if 'Erkek:' in text and 'Kadın:' in text:
        if gender == "Erkek":
            m = re.search(r'Erkek:\s*([\d.,]+)\s*-\s*([\d.,]+)', text)
        else:
            m = re.search(r'Kadın:\s*([\d.,]+)\s*-\s*([\d.,]+)', text)
        if m:
            return (_normalize_number(m.group(1)), _normalize_number(m.group(2)))

    # "veya" içerenler: mutlak sayıyı kullan
    if 'veya' in text:
        ilk = text.split('veya')[0]
        m = re.search(r'([\d.,]+)\s*-\s*([\d.,]+)', ilk)
        if m:
            return (_normalize_number(m.group(1)), _normalize_number(m.group(2)))

    # Saf yüzde aralık
    pct = re.search(r'%\s*([\d.,]+)\s*-\s*%?\s*([\d.,]+)', text)
    if pct:
        return (_normalize_number(pct.group(1)), _normalize_number(pct.group(2)))

    # Standart aralık
    std = re.search(r'([\d.,]+)\s*-\s*([\d.,]+)', text)
    if std:
        return (_normalize_number(std.group(1)), _normalize_number(std.group(2)))

    # "< X" formatı
    lt = re.search(r'<\s*%?\s*([\d.,]+)', text.split(';')[0])
    if lt:
        return (0.0, _normalize_number(lt.group(1)))

    return None


def extract_expected_unit(text):
    """normal_aralik metninden beklenen birimi çıkar."""
    if not text:
        return None
    m = re.search(
        r'(mg/dL|g/dL|U/L|mIU/L|mEq/L|mmol/L|fL|pg|%|/µL|milyon/µL|IU/L|ms|atım/dakika|/dk|mmHg|°C|mg/L)',
        text
    )
    return m.group(1) if m else None


# ================================================================
# BÖLÜM 3: ANA FACT-CHECK MOTORU
# ================================================================

class MedicalFactChecker:
    """AI yanıtlarını tıbbi doğruluk açısından denetleyen kural motoru."""

    # Durum ile UYUMSUZ anahtar kelimeler (çelişki tespiti)
    # NOT: "eksikliği" gibi kelimeler Yüksek durumda neden olabilir
    #   (ör: Demir eksikliği → PLT yüksek), bu yüzden çıkarıldı.
    CONTRADICTION_PATTERNS = {
        "Normal": {
            "negatif": [
                "tehlikeli", "acil müdahale gerekir", "ciddi risk",
                "hayatı tehdit", "diyaliz gerekebilir", "transfüzyon gerektirebilir",
                "komplikasyon riski", "organ hasarı", "acil tedavi"
            ]
        },
        "Yüksek": {
            "negatif": [
                "düşük olduğunu gösterir", "hipoglisemi belirtisidir",
                "hipokalemi", "hiponatremi"
            ]
        },
        "Düşük": {
            "negatif": [
                "yüksek seyrettiğini gösterir", "hiperkalemi",
                "hipernatremi", "diyabet tanı veya kontrol"
            ]
        }
    }

    def __init__(self, dict_dir="."):
        """Sözlükleri yükle."""
        self.sozluk = {}
        self.dict_dir = dict_dir

        for fname in ['biyokimya.json', 'hemogram.json', 'ekg.json', 'epikriz.json']:
            fpath = os.path.join(dict_dir, fname)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        self.sozluk.update(data)
                    except json.JSONDecodeError:
                        pass

        print(f"FactChecker: {len(self.sozluk)} test tanımı yüklendi.")

    # ------------------------------------------
    # KATMAN 1: Değer-Durum Uyumu
    # ------------------------------------------
    def _check_value_status(self, test_name, value, stated_status, gender, report):
        """Sayısal değer ile belirtilen durum (Normal/Yüksek/Düşük) eşleşiyor mu?"""
        report.checks_total += 1

        info = self.sozluk.get(test_name)
        if not info:
            return  # Sözlükte yoksa bu kontrolü atla

        aralik_text = info.get("normal_aralik", "")
        rng = parse_range(aralik_text, gender)
        if not rng:
            return  # Parse edilemiyorsa atla

        lo, hi = rng

        # Gerçek durumu hesapla
        if value < lo:
            actual = "Düşük"
        elif value > hi:
            actual = "Yüksek"
        else:
            actual = "Normal"

        if actual != stated_status:
            report.findings.append(Finding(
                severity=Severity.ERROR,
                category="Değer-Durum Uyumu",
                test_name=test_name,
                message=f"Değer {value} → gerçek durum '{actual}' ama '{stated_status}' denmiş. "
                        f"Referans: {lo}-{hi}",
                suggestion=f"Durumu '{actual}' olarak düzeltin."
            ))
        else:
            report.checks_passed += 1

    # ------------------------------------------
    # KATMAN 2: Birim Doğruluğu
    # ------------------------------------------
    def _check_unit(self, test_name, stated_unit, report):
        """Test için doğru birim kullanılmış mı?"""
        report.checks_total += 1

        info = self.sozluk.get(test_name)
        if not info:
            return

        expected = extract_expected_unit(info.get("normal_aralik", ""))
        if not expected:
            report.checks_passed += 1
            return

        # Birim normalleştirme
        unit_map = {
            "milyon/µL": "milyon/µL",
            "/µL": "/µL",
            "ml": "mL",
        }
        stated_norm = unit_map.get(stated_unit, stated_unit)
        expected_norm = unit_map.get(expected, expected)

        if stated_norm and stated_norm != expected_norm:
            # Birimin tamamen farklı olup olmadığını kontrol et
            if stated_norm.lower() not in expected_norm.lower() and expected_norm.lower() not in stated_norm.lower():
                report.findings.append(Finding(
                    severity=Severity.ERROR,
                    category="Birim Doğruluğu",
                    test_name=test_name,
                    message=f"Birim '{stated_unit}' ama beklenen '{expected}'.",
                    suggestion=f"Birimi '{expected}' olarak düzeltin."
                ))
                return

        report.checks_passed += 1

    # ------------------------------------------
    # KATMAN 3: Kritik Değer Tespiti
    # ------------------------------------------
    def _check_critical_values(self, test_name, value, explanation, report):
        """Tehlikeli eşikler aşılmışsa açıklamada uyarı var mı?"""
        report.checks_total += 1

        info = self.sozluk.get(test_name)
        if not info:
            report.checks_passed += 1
            return

        tehlikeli = info.get("tehlikeli_deger", "")
        if not tehlikeli:
            report.checks_passed += 1
            return

        thresholds = parse_tehlikeli_deger(tehlikeli)
        is_critical = False

        for op, threshold, desc in thresholds:
            if op in ('<', '≤') and value < threshold:
                is_critical = True
            elif op in ('>', '≥') and value > threshold:
                is_critical = True

        if is_critical:
            # Açıklamada tehlike uyarısı var mı?
            uyari_kelimeleri = [
                "acil", "tehlikeli", "risk", "kritik", "hayatı tehdit",
                "diyaliz", "transfüzyon", "müdahale", "koma", "arrest",
                "bilinç", "ölüm"
            ]
            explanation_lower = explanation.lower()
            has_warning = any(k in explanation_lower for k in uyari_kelimeleri)

            if not has_warning:
                report.findings.append(Finding(
                    severity=Severity.WARNING,
                    category="Kritik Değer",
                    test_name=test_name,
                    message=f"Değer {value} tehlikeli eşikte ({tehlikeli}) "
                            f"ama açıklamada acil uyarı yok!",
                    suggestion="Açıklamaya 'Bu değer tehlikeli aralıktadır, acil tıbbi değerlendirme gerekir.' ekleyin."
                ))
                return

        report.checks_passed += 1

    # ------------------------------------------
    # KATMAN 4: Cinsiyet Tutarlılığı
    # ------------------------------------------
    def _check_gender_consistency(self, test_name, gender, explanation, report):
        """Cinsiyete özel referans aralıkları doğru kullanılmış mı?"""
        report.checks_total += 1

        info = self.sozluk.get(test_name)
        if not info:
            report.checks_passed += 1
            return

        aralik_text = info.get("normal_aralik", "")
        # Sadece cinsiyete göre değişen testlerde kontrol et
        if 'Erkek:' not in aralik_text or 'Kadın:' not in aralik_text:
            report.checks_passed += 1
            return

        # Açıklamada yanlış cinsiyetin referansı kullanılmış mı?
        if gender == "Kadın" and "Erkek:" in explanation:
            # Eğer her iki cinsiyeti de gösteren genel referans gösteriyorsa sorun yok
            if "Kadın:" not in explanation:
                report.findings.append(Finding(
                    severity=Severity.ERROR,
                    category="Cinsiyet Tutarlılığı",
                    test_name=test_name,
                    message=f"Hasta Kadın ama açıklamada sadece Erkek referansı kullanılmış.",
                    suggestion="Kadın için doğru referans aralığını kullanın."
                ))
                return

        report.checks_passed += 1

    # ------------------------------------------
    # KATMAN 5: Açıklama Tutarlılığı (Çelişki)
    # ------------------------------------------
    def _check_contradictions(self, test_name, status, explanation, report):
        """Durum ile açıklama arasında çelişki var mı?"""
        report.checks_total += 1

        patterns = self.CONTRADICTION_PATTERNS.get(status, {})
        neg_patterns = patterns.get("negatif", [])

        explanation_lower = explanation.lower()
        found_contradictions = []

        for pattern in neg_patterns:
            if pattern.lower() in explanation_lower:
                found_contradictions.append(pattern)

        if found_contradictions:
            report.findings.append(Finding(
                severity=Severity.ERROR,
                category="Çelişki Tespiti",
                test_name=test_name,
                message=f"Durum '{status}' ama açıklamada çelişen ifadeler: "
                        f"{', '.join(found_contradictions)}",
                suggestion="Açıklamayı test durumu ile uyumlu hale getirin."
            ))
        else:
            report.checks_passed += 1

    # ------------------------------------------
    # KATMAN 6: Halüsinasyon Tespiti
    # ------------------------------------------
    def _check_hallucination(self, test_name, explanation, report):
        """Sözlükte tanımlı olmayan test veya açıklama kullanılmış mı?"""
        report.checks_total += 1

        if test_name not in self.sozluk:
            report.findings.append(Finding(
                severity=Severity.WARNING,
                category="Halüsinasyon",
                test_name=test_name,
                message=f"'{test_name}' test sözlükte tanımlı değil — AI uydurmuş olabilir!",
                suggestion="Bu testin gerçekliğini kontrol edin veya sözlüğe ekleyin."
            ))
            return

        # Sözlükteki açıklama ile AI açıklaması arasında tutarlılık
        info = self.sozluk[test_name]
        sade = (info.get("sade_aciklama") or "").lower()

        # AI açıklamasında sade_aciklama'nın ana konusu geçiyor mu?
        # (Basit kelime eşleştirme — tam NLP yerine pragmatik yaklaşım)
        tam_adi = (info.get("tam_adi") or "").lower()
        if tam_adi and len(tam_adi) > 5:
            # tam_adi'nın en az bir parçası açıklamada geçmeli
            parts = [p.strip() for p in re.split(r'[/()]', tam_adi) if len(p.strip()) > 3]
            found_any = any(p in explanation.lower() for p in parts)
            if not found_any:
                report.findings.append(Finding(
                    severity=Severity.INFO,
                    category="Halüsinasyon",
                    test_name=test_name,
                    message=f"Açıklamada test adı referansı bulunamadı. "
                            f"Beklenen: '{info.get('tam_adi')}'",
                    suggestion="Test adının tam halini açıklamaya ekleyin."
                ))
                return

        report.checks_passed += 1

    # ------------------------------------------
    # ANA KONTROL FONKSİYONU
    # ------------------------------------------
    def check_ai_response(self, text):
        """
        AI yanıt metnini parse ederek tüm kontrolleri uygular.
        
        Beklenen format (JSONL satırı veya düz metin):
          [USER]
          Hasta Bilgileri: 72 yaşında, Kadın.
          Laboratuvar Sonuçları:
          - Glukoz: 85.3 mg/dL (Normal)
          
          [ASSISTANT]
          **Açlık Kan Şekeri (Glukoz)**: ...
        """
        report = FactCheckReport()

        # Cinsiyet çıkar
        gender = "Erkek"
        if "Kadın" in text:
            gender = "Kadın"

        # Test sonuçlarını parse et
        test_pattern = re.findall(
            r'-\s*(\w+):\s*([\d.,]+)\s*(\S*)\s*\((Normal|Yüksek|Düşük)\)',
            text
        )

        if not test_pattern:
            report.findings.append(Finding(
                severity=Severity.INFO,
                category="Parse",
                test_name="-",
                message="Metin içinde test sonucu bulunamadı.",
            ))
            return report

        # Açıklama bölümünü ayır
        assistant_text = ""
        if "[ASSISTANT]" in text:
            assistant_text = text.split("[ASSISTANT]")[-1]
        elif "assistant" in text.lower():
            assistant_text = text
        else:
            assistant_text = text

        # Her test için açıklama bölümünü ayrı ayrı çıkar
        # Format: "**Test Adı**: açıklama..." şeklinde
        def extract_test_explanation(test_name, full_text):
            """Asistan metninden ilgili testin açıklamasını çıkar."""
            info = self.sozluk.get(test_name, {})
            tam_adi = info.get("tam_adi", test_name)
            
            # **Tam Adı**: ... ile başlayan bloğu bul
            # Bir sonraki **'ya veya metnin sonuna kadar al
            patterns_to_try = [
                re.escape(tam_adi),
                re.escape(test_name),
            ]
            for p in patterns_to_try:
                match = re.search(
                    rf'\*\*{p}\*\*:?\s*(.*?)(?=\n\*\*|$)',
                    full_text, re.DOTALL
                )
                if match:
                    return match.group(1).strip()
            return full_text  # Bulunamazsa tüm metni döndür

        for test_name, value_str, unit, stated_status in test_pattern:
            try:
                # Binlik ayraç temizle (359.141 → 359141)
                clean_val = value_str.replace('.', '')
                # Eğer ondalık kısım varsa (tek nokta) onu koru
                if value_str.count('.') == 1 and len(value_str.split('.')[-1]) != 3:
                    value = float(value_str)
                else:
                    value = float(clean_val) if clean_val else 0
            except ValueError:
                continue

            # NaN birim kontrolü
            if unit.lower() in ('nan', ''):
                unit = ""

            # Bu teste ait açıklamayı çıkar
            test_explanation = extract_test_explanation(test_name, assistant_text)

            # Her test için tüm katmanları çalıştır
            self._check_value_status(test_name, value, stated_status, gender, report)
            self._check_unit(test_name, unit, report)
            self._check_critical_values(test_name, value, test_explanation, report)
            self._check_gender_consistency(test_name, gender, test_explanation, report)
            self._check_contradictions(test_name, stated_status, test_explanation, report)
            self._check_hallucination(test_name, assistant_text, report)

        return report

    def check_jsonl_file(self, filepath, max_lines=None):
        """
        Tüm JSONL dosyasını toplu kontrol eder.
        Her satır için rapor üretir, sonunda özet verir.
        """
        total_report = FactCheckReport()
        line_errors = {}

        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if max_lines and i >= max_lines:
                    break

                try:
                    data = json.loads(line)
                    messages = data.get("messages", [])
                    if len(messages) < 3:
                        continue

                    user_msg = messages[1].get("content", "")
                    asst_msg = messages[2].get("content", "")
                    full_text = f"[USER]\n{user_msg}\n[ASSISTANT]\n{asst_msg}"

                    report = self.check_ai_response(full_text)

                    total_report.checks_total += report.checks_total
                    total_report.checks_passed += report.checks_passed

                    if report.errors or report.warnings:
                        line_errors[i + 1] = report
                        total_report.findings.extend(report.findings)

                except json.JSONDecodeError:
                    total_report.findings.append(Finding(
                        severity=Severity.ERROR,
                        category="JSON",
                        test_name="-",
                        message=f"Satır {i+1}: Geçersiz JSON."
                    ))

        # Özet rapor
        print("=" * 65)
        print("  TOPLU JSONL FACT-CHECK RAPORU")
        print("=" * 65)
        print(f"\n📊 GENEL ÖZET")
        print(f"   Kontrol edilen satır: {i + 1 if 'i' in dir() else 0}")
        print(f"   Toplam kontrol:       {total_report.checks_total}")
        print(f"   Başarılı:             {total_report.checks_passed}")
        print(f"   Güvenilirlik:         %{total_report.score}")

        error_count = len(total_report.errors)
        warn_count = len(total_report.warnings)
        print(f"\n   {Severity.ERROR.value}: {error_count}")
        print(f"   {Severity.WARNING.value}: {warn_count}")

        if line_errors:
            print(f"\n📋 SORUNLU SATIRLAR (ilk 10):")
            for line_no, rep in list(line_errors.items())[:10]:
                err_msgs = [f.message[:80] for f in rep.errors[:2]]
                warn_msgs = [f.message[:80] for f in rep.warnings[:2]]
                print(f"   Satır {line_no}:")
                for m in err_msgs:
                    print(f"      ❌ {m}")
                for m in warn_msgs:
                    print(f"      ⚠️  {m}")
        else:
            print(f"\n✅ TÜM SATIRLAR DOĞRULAMA TESTLERİNİ GEÇTİ!")

        print("\n" + "=" * 65)
        return total_report


# ================================================================
# BÖLÜM 4: TEK BAŞINA ÇALIŞTIRMA
# ================================================================

if __name__ == "__main__":
    import sys

    checker = MedicalFactChecker()

    # Komut satırından dosya verilmişse toplu kontrol
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        max_lines = int(sys.argv[2]) if len(sys.argv) > 2 else None
        checker.check_jsonl_file(filepath, max_lines)
    else:
        # Varsayılan: training_data.jsonl dosyasını kontrol et
        if os.path.exists("training_data.jsonl"):
            print("\n🔍 training_data.jsonl dosyası kontrol ediliyor...\n")
            checker.check_jsonl_file("training_data.jsonl")
        else:
            # Demo: Tek bir örnek kontrol et
            print("\n🔍 Demo kontrol çalıştırılıyor...\n")
            demo = """[USER]
Hasta Bilgileri: 65 yaşında, Kadın.
Laboratuvar Sonuçları:
- Glukoz: 85.3 mg/dL (Yüksek)
- Potasyum: 7.2 mEq/L (Normal)
- Kreatinin: 1.5 fL (Normal)

[ASSISTANT]
**Glukoz**: Kan şekeriniz normal aralıktadır.
**Potasyum**: Değeriniz normaldir, endişeye gerek yok.
**Kreatinin**: Böbrek fonksiyonlarınız normaldir."""

            report = checker.check_ai_response(demo)
            report.yazdir()
