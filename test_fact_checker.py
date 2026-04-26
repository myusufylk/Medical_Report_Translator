"""
Fact-Checker Test Senaryoları
AI'ın doğru ve yanlış yanıtlarını test eder.
"""
from medical_fact_checker import MedicalFactChecker

checker = MedicalFactChecker()

# ============================================================
# SENARYO 1: TAMAMEN DOĞRU YANIT
# ============================================================
print("\n" + "🟢" * 30)
print("SENARYO 1: Doğru AI Yanıtı")
print("🟢" * 30)

dogru = """[USER]
Hasta Bilgileri: 55 yaşında, Erkek.
Laboratuvar Sonuçları:
- Glukoz: 85.0 mg/dL (Normal)
- Kreatinin: 1.0 mg/dL (Normal)
- ALT: 25.0 U/L (Normal)

[ASSISTANT]
**Açlık Kan Şekeri (Glukoz) / Fasting Blood Glucose**: Kanınızdaki şeker seviyesini gösterir. Değer normal referans aralığında (70 – 100 mg/dL) yer almaktadır.
**Kreatinin / Creatinine**: Böbreklerinizin ne kadar iyi çalıştığını gösterir. Değer normal referans aralığında (Erkek: 0,7 – 1,3 mg/dL; Kadın: 0,6 – 1,1 mg/dL) yer almaktadır.
**Alanin Aminotransferaz / Alanine Aminotransferase (ALT/SGPT)**: Karaciğer hasarını gösteren en spesifik enzimlerden biridir. Değer normal referans aralığında yer almaktadır."""

r1 = checker.check_ai_response(dogru)
r1.yazdir()


# ============================================================
# SENARYO 2: DEĞER-DURUM UYUMSUZLUĞU (AI yanlış durum söylüyor)
# ============================================================
print("\n" + "🔴" * 30)
print("SENARYO 2: AI Yanlış Durum Söylüyor")
print("🔴" * 30)

yanlis_durum = """[USER]
Hasta Bilgileri: 60 yaşında, Kadın.
Laboratuvar Sonuçları:
- Glukoz: 85.0 mg/dL (Yüksek)
- Potasyum: 7.2 mEq/L (Normal)
- HbA1c: 4.5 % (Yüksek)

[ASSISTANT]
**Açlık Kan Şekeri (Glukoz) / Fasting Blood Glucose**: Diyabet düşünülebilir. Stres veya enfeksiyon geçici yükseltebilir.
**Potasyum / Potassium (K)**: Değeriniz normaldir, endişeye gerek yoktur.
**Glikozile Hemoglobin / Glycated Hemoglobin (HbA1c)**: Kan şekerinin uzun süre yüksek seyrettiğini gösterir."""

r2 = checker.check_ai_response(yanlis_durum)
r2.yazdir()


# ============================================================
# SENARYO 3: YANLIŞ BİRİM
# ============================================================
print("\n" + "🟡" * 30)
print("SENARYO 3: Yanlış Birim Kullanımı")
print("🟡" * 30)

yanlis_birim = """[USER]
Hasta Bilgileri: 45 yaşında, Erkek.
Laboratuvar Sonuçları:
- Kreatinin: 1.5 fL (Yüksek)
- HGB: 14.0 mEq/L (Normal)

[ASSISTANT]
**Kreatinin / Creatinine**: Böbreklerinizin ne kadar iyi çalıştığını gösterir. Böbrek fonksiyon bozukluğu düşünülebilir.
**Hemoglobin / Hemoglobin**: Kırmızı kan hücrelerinin oksijen taşıyan proteinidir. Değer normaldir."""

r3 = checker.check_ai_response(yanlis_birim)
r3.yazdir()


# ============================================================
# SENARYO 4: KRİTİK DEĞER UYARISI EKSİK
# ============================================================
print("\n" + "🟠" * 30)
print("SENARYO 4: Kritik Değer — Uyarı Eksik")
print("🟠" * 30)

kritik = """[USER]
Hasta Bilgileri: 70 yaşında, Kadın.
Laboratuvar Sonuçları:
- Potasyum: 7.0 mEq/L (Yüksek)
- Glukoz: 450.0 mg/dL (Yüksek)
- Sodyum: 115.0 mEq/L (Düşük)

[ASSISTANT]
**Potasyum / Potassium (K)**: Potasyumunuz biraz yüksek, beslenmenize dikkat edin.
**Açlık Kan Şekeri (Glukoz) / Fasting Blood Glucose**: Kan şekeriniz yüksek, diyabet olabilir.
**Sodyum / Sodium (Na)**: Sodyumunuz düşük, su içmeyi azaltın."""

r4 = checker.check_ai_response(kritik)
r4.yazdir()


# ============================================================
# SENARYO 5: CİNSİYET UYUMSUZLUĞU
# ============================================================
print("\n" + "🟣" * 30)
print("SENARYO 5: Cinsiyet Referans Hatası")
print("🟣" * 30)

cinsiyet = """[USER]
Hasta Bilgileri: 50 yaşında, Kadın.
Laboratuvar Sonuçları:
- Kreatinin: 1.2 mg/dL (Normal)
- GGT: 50.0 U/L (Normal)

[ASSISTANT]
**Kreatinin / Creatinine**: Böbrek fonksiyonlarınız normaldir. Değer normal referans aralığında (Erkek: 0,7 – 1,3 mg/dL) yer almaktadır.
**Gama-Glutamil Transferaz / Gamma-Glutamyl Transferase**: Karaciğer enziminiz normaldir."""

r5 = checker.check_ai_response(cinsiyet)
r5.yazdir()


# ============================================================
# SENARYO 6: HALÜSİNASYON (Uydurma Test)
# ============================================================
print("\n" + "👻" * 30)
print("SENARYO 6: Halüsinasyon — Uydurma Test")
print("👻" * 30)

halusin = """[USER]
Hasta Bilgileri: 35 yaşında, Erkek.
Laboratuvar Sonuçları:
- Glukoz: 95.0 mg/dL (Normal)
- Nörotransmiteraz: 45.0 U/L (Yüksek)

[ASSISTANT]
**Açlık Kan Şekeri (Glukoz) / Fasting Blood Glucose**: Kan şekeriniz normal aralıktadır.
**Nörotransmiteraz**: Beyin sinir iletimi enzimi normalin üstündedir. Nörolojik hastalık düşünülebilir."""

r6 = checker.check_ai_response(halusin)
r6.yazdir()


# ============================================================
# SENARYO 7: ÇELİŞKİLİ AÇIKLAMA
# ============================================================
print("\n" + "💥" * 30)
print("SENARYO 7: Çelişkili Açıklama")
print("💥" * 30)

celiskili = """[USER]
Hasta Bilgileri: 65 yaşında, Erkek.
Laboratuvar Sonuçları:
- Glukoz: 85.0 mg/dL (Normal)

[ASSISTANT]
**Açlık Kan Şekeri (Glukoz) / Fasting Blood Glucose**: Değeriniz acil müdahale gerekir seviyesindedir. Organ hasarı riski vardır. Derhal hastaneye başvurun."""

r7 = checker.check_ai_response(celiskili)
r7.yazdir()
