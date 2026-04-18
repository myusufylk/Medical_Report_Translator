# YMH212 - Medikal Rapor Tercümanı
## Bölüm 1: Problem Tanımı ve Kapsam Gerekçelendirmesi

### 1. Problem Tanımı: Hastalarda Bilgi Asimetrisi ve Siberkondri
Günümüzde hastanelerde üretilen tıbbi raporlar (Hemogram, Biyokimya, Epikriz ve EKG ritim sonuçları) tamamen sağlık profesyonellerinin kendi aralarındaki iletişimi sağlamak amacıyla, ağır bir tıbbi terminoloji (jargon) ile yazılmaktadır. 

Bu durum, sağlık sistemi ile hasta arasında ciddi bir **"Bilgi Asimetrisi"** yaratmaktadır. Raporunu e-Nabız veya hastane bankosundan alan bir hasta, kendi sağlık durumu hakkındaki metni okuyamamakta ve anlayamamaktadır. Polikliniklerdeki yoğunluk sebebiyle hekimlerin her bir hastaya tahlil detaylarını uzun uzun anlatacak vakti bulamaması, hastaları internet üzerinden kendi başlarına araştırma yapmaya itmektedir. 

Bu kontrolsüz araştırma süreci, tıbbi literatürde **Siberkondri** (internette hastalık araştırarak anksiyete ve panik yaşama durumu) olarak bilinen probleme yol açmaktadır. Basit bir referans dışı değer, internet aramalarında hastanın karşısına "kanser" veya "kronik yetmezlik" gibi korkutucu ve yanlış teşhisler olarak çıkabilmektedir.

**Çözüm İhtiyacı:** Hastaların tahlil ve taburcu (epikriz) raporlarını, tıbbi geçerliliğini kaybetmeden, halk dilinde ve anında özetleyebilecek; sınırları (kapsamı) net çizilmiş, halüsinasyon riski sıfıra indirilmiş ve herkes için erişilebilir (görme engelli dostu) bir yapay zeka köprüsüne ihtiyaç vardır.

---

### 2. Hedef Kitle ve Kullanıcı Personaları
Projenin arayüzü (UI) ve kullanıcı deneyimi (UX), aşağıdaki iki temel kullanıcı profiline (Persona) göre tasarlanmıştır:

#### 🧑🏻‍🦳 Persona 1: "Teknolojiye Mesafeli, Endişeli Hasta"
* **İsim/Yaş:** Ahmet Yılmaz, 50 Yaşında.
* **Profil:** Emekli memur. Akıllı telefon kullanabiliyor ancak karmaşık uygulamalardan çekiniyor. Sağlık durumuyla ilgili evhamlı bir yapıya sahip.
* **Senaryo:** Hastanede kan tahlili (Hemogram) yaptırdı. Sonuçları e-Nabız'a düştü ancak "Eozinofil", "MCH", "HCT" gibi terimlerin ne anlama geldiğini bilmiyor. İnternette araştırıp kötü hastalıklara yakalandığını düşünerek panik oluyor. Doktor randevusuna daha 2 gün var.
* **Sistemden Beklentisi:** Kayıt olma, şifre girme gibi karmaşık adımlarla uğraşmadan, tek bir büyük butonla raporunun fotoğrafını çekip anında "Endişe edilecek bir durum yok, şu değeriniz hafif yüksek, doktorunuzla görüşün" şeklinde insani bir özet almak.

#### 👵🏼 Persona 2: "Erişilebilirlik İhtiyacı Olan Hasta"
* **İsim/Yaş:** Ayşe Demir, 65 Yaşında.
* **Profil:** Ev hanımı. Gözlerinde yaşa bağlı presbiyopi (yakını görememe) ve başlangıç seviyesinde katarakt var. Telefon ekranındaki küçük yazıları okumakta çok zorlanıyor.
* **Senaryo:** Bir hafta hastanede yattıktan sonra taburcu oldu. Kendisine verilen Epikriz (Taburcu) raporundaki uzun metinleri okuyamıyor. İlaçlarını veya evde neye dikkat etmesi gerektiğini anlatan yazıları torununa okutmak zorunda kalıyor.
* **Sistemden Beklentisi:** Sadece metni basitleştiren bir uygulama değil; aynı zamanda çevrilen o basit metni yüksek sesle ve anlaşılır bir diksiyonla kendisine okuyacak bir **"Sesli Okuma (Text-to-Speech)"** asistanı arıyor. (Sistemimizdeki Erişilebilirlik/Sesli Okuma özelliği tam olarak bu persona için geliştirilmiştir.)