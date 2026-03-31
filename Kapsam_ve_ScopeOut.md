# 🩺 Medikal Rapor Tercümanı  
### Kapsam ve Scope Out

![Status](https://img.shields.io/badge/Status-Planning-blue)
![Project Scope](https://img.shields.io/badge/Scope-Defined-success)
![Document](https://img.shields.io/badge/Document-Markdown-informational)

---

## 📌 Proje Amacı

Bu projenin amacı, kullanıcıların sağlık kurumlarından aldıkları medikal raporları daha **anlaşılır**, **sade** ve **günlük dile yakın** şekilde yorumlayabilen bir sistem geliştirmektir.

Birçok kullanıcı, medikal raporlarda yer alan teknik terimleri, kısaltmaları ve değerleri anlamakta zorlanmaktadır.  
Bu proje, kullanıcıların yüklediği raporları analiz ederek daha anlaşılır açıklamalar sunmayı hedeflemektedir.

> Amaç, kullanıcıyı **bilgilendirmek** ve raporu daha iyi anlamasına yardımcı olmaktır.

---

## 🎯 Proje Kapsamı (Scope)

Bu proje kapsamında sistem, kullanıcı tarafından yüklenen belirli medikal belge türlerini işleyerek sadeleştirilmiş ve açıklayıcı çıktılar üretecektir.

### Sistem kapsamında yer alan temel özellikler:

- 📷 Kullanıcının raporunu **fotoğraf veya PDF** olarak yükleyebilmesi
- 🔍 Belge içeriğinin **OCR (Optik Karakter Tanıma)** ile okunabilmesi
- 🤖 Okunan verilerin **Yapay Zekâ / NLP** yardımıyla sadeleştirilmesi
- 📝 Kullanıcıya teknik olmayan, anlaşılır açıklamalar sunulması
- 📑 Belirli rapor türlerine özel yorumlama yapılması

---

# 🧾 Desteklenen Rapor Türleri

Bu proje kapsamında sistem yalnızca aşağıdaki **3 ana rapor türü** üzerinde çalışacaktır:

---

## 1️⃣ Kan Tahlil Sonuçları

Sistem, kan tahlili sonuçlarında yer alan laboratuvar değerlerini okuyarak kullanıcıya daha anlaşılır açıklamalar sunacaktır.

### Bu kapsamda hedeflenenler:
- Hemogram, biyokimya ve temel kan test sonuçlarının okunması
- Referans dışı görünen değerlerin sade bir dille açıklanması
- Tahlilde yer alan kısaltmaların (ör. **HGB, WBC, GLU**) anlaşılır hale getirilmesi
- Kullanıcının rapordaki değerlerin ne anlama geldiğini daha kolay anlaması

### Örnek açıklama türleri:
- “Bu değer referans aralığının biraz üstünde görünüyor.”
- “Bu test kandaki şeker düzeyini gösterir.”
- “Bu sonuç doktor değerlendirmesi gerektirebilir.”

---

## 2️⃣ Epikriz Raporları

Sistem, hastane çıkış özeti veya tedavi sürecini açıklayan epikriz raporlarını daha sade ve günlük dile yakın biçimde özetleyecektir.

### Bu kapsamda hedeflenenler:
- Uzun ve karmaşık epikriz metinlerinin özetlenmesi
- Tıbbi ifadelerin daha anlaşılır hale getirilmesi
- Hastanede yapılan işlem, gözlem veya uygulamaların kullanıcıya açıklanması
- Kullanıcının raporun genel içeriğini ve sürecini daha iyi anlaması

### Örnek açıklama türleri:
- “Bu raporda hastanede uygulanan tedavi süreci anlatılıyor.”
- “Burada doktor, hastanın hastaneye geliş nedeni ve uygulanan işlemleri özetlemiş.”
- “Raporun bu kısmı taburculuk sonrası önerileri içeriyor olabilir.”

---

## 3️⃣ EKG Raporları

Sistem, EKG raporlarında yer alan **metinsel açıklamaları** daha anlaşılır şekilde yorumlamayı hedeflemektedir.

### Bu kapsamda hedeflenenler:
- EKG raporundaki yazılı sonuçların okunması
- “Sinüs ritmi”, “taşikardi”, “bradikardi” gibi ifadelerin sadeleştirilmesi
- Kullanıcının EKG raporunda geçen temel kavramları anlamasına yardımcı olunması
- Teknik terimlerin panik oluşturmadan açıklanması

> **Not:** Bu proje, EKG’nin grafik dalga formunu uzman seviyesinde analiz etmeyi değil; öncelikli olarak raporda yer alan **yazılı sonuçların açıklanmasını** hedeflemektedir.

---

## 👥 Hedef Kullanıcı Kitlesi

Bu proje aşağıdaki kullanıcı gruplarını hedeflemektedir:

- Medikal raporlarını anlamakta zorlanan bireyler
- Tıbbi terimlere aşina olmayan hastalar
- Hastane veya laboratuvar sonuçlarını daha anlaşılır görmek isteyen kullanıcılar
- Kendi sağlık belgeleri hakkında temel bilgi edinmek isteyen bireyler

---

## 📤 Sistemden Beklenen Çıktılar

Sistemden beklenen temel çıktılar şunlardır:

- sadeleştirilmiş açıklama
- kısa özet
- temel terim açıklamaları
- kullanıcı dostu bilgilendirme metni

> Sistem, teknik rapor dilini herkesin anlayabileceği bir dile çevirmeyi amaçlamaktadır.

---

# 🚫 Scope Out (Proje Dışında Kalanlar)

Bu proje kapsamında **yer almayacak** özellikler şunlardır:

- ❌ Kullanıcıya **kesin teşhis koymak**
- ❌ Hastalık hakkında **kesin tıbbi karar vermek**
- ❌ Kullanıcıya **tedavi planı oluşturmak**
- ❌ **İlaç önerisinde bulunmak**
- ❌ Doktor yerine geçecek bir sistem geliştirmek
- ❌ Tüm tıbbi branş ve belge türlerini desteklemek
- ❌ MR, tomografi, röntgen gibi tüm görüntüleme raporlarını kapsamlı şekilde yorumlamak
- ❌ Gerçek zamanlı doktor desteği veya canlı uzman bağlantısı sunmak
- ❌ Hastane bilgi sistemleri ile tam entegrasyon sağlamak
- ❌ Acil durum yönlendirme ve tıbbi müdahale desteği vermek

---

## ⚙️ Teknik Sınırlılıklar

Bu proje aşağıdaki teknik sınırlılıklar çerçevesinde geliştirilecektir:

- OCR başarısı, yüklenen belge kalitesine bağlı olarak değişebilir
- Farklı hastanelerde kullanılan rapor formatları değişkenlik gösterebilir
- Yapay zekâ tarafından oluşturulan açıklamalar yalnızca **bilgilendirme amaçlıdır**
- Bazı tıbbi ifadeler bağlama göre farklı anlam taşıyabileceğinden, nihai yorum için doktor değerlendirmesi gereklidir
- Sistem, uzman tıbbi karar mekanizması yerine kullanıcı dostu açıklama sağlamayı hedeflemektedir

---

## ✅ Sonuç

Bu proje, kullanıcıların medikal raporlarını daha kolay anlamasını sağlayan yardımcı bir sistem geliştirmeyi amaçlamaktadır.

Sistem özellikle şu üç ana belge türüyle sınırlandırılmıştır:

- **Kan Tahlil Sonuçları**
- **Epikriz Raporları**
- **EKG Raporları**

> Projenin amacı **teşhis veya tedavi sunmak değil**, karmaşık medikal bilgiyi daha sade, anlaşılır ve kullanıcı dostu hale getirmektir.
