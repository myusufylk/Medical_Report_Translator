import 'dart:typed_data';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:google_generative_ai/google_generative_ai.dart';

class GeminiService {
  late final GenerativeModel _model;

  GeminiService() {
    final apiKey = dotenv.env['GEMINI_API_KEY'];
    if (apiKey == null || apiKey.isEmpty) {
      throw Exception('GEMINI_API_KEY bulunamadı. Lütfen .env dosyasını kontrol edin.');
    }

    _model = GenerativeModel(
      model: 'gemini-2.5-flash',
      apiKey: apiKey,
    );
  }

  Future<String> analyzeReport(Uint8List imageBytes, String reportType) async {
    try {
      final imagePart = DataPart('image/jpeg', imageBytes);

      final prompt = TextPart('''
Sen uzman bir doktorsun ancak hastalarla olabildiğince sade, anlaşılır ve şefkatli bir dille konuşuyorsun.
Aşağıda sana yüklenen $reportType belgesi var.

Lütfen yanıtını akıcı ve doğal bir metin olarak, şu sırayla ver ("Bölüm 1" gibi mekanik başlıklar KULLANMA):

1. Önce hastaya mutlaka "Sağlıklı günler! / Geçmiş olsun!" gibi içten bir dilekle başla.
2. Ardından tahlil/rapor değerlerinin geneli hakkında sadece TEK CÜMLELİ, rahatlatıcı genel bir yorum yap (Örn: "Genel olarak tablonuz fena durmuyor ancak ufak detaylar var").
3. Sonra SADECE anormal (referans aralığı dışı, düşük veya yüksek) çıkan değerleri ele al ve bunların ne anlama geldiğini tıbbi terimlere boğmadan kısaca açıkla.her değer için ayrı ayrı açıklama yap hepsi tek tek maddeler halinde olsun. Normal çıkan hiçbir şeye değinme.
4. En sonda (metnin bittiği kısımda), bu anormal değerleri iyileştirebilmesi için beslenme ve doğal yaşam tarzına yönelik NET tavsiyelerde bulun ("Şu değer düşük, bunu artırmak için bol portakal ye" gibi). ve bu tavsiyeleri de maddeler halinde yaz.
5. Bu tavsiyeleri verirken KESİNLİKLE eczane ilacı veya tıbbi bir tedavi (Aspirin vb.) ÖNERME.
6. Cümleni/Metnini bitirirken, kesin teşhis ve tedavi için hastayı mutlaka kendi hekimine görünmesi gerektiği konusunda dostça uyar.
''');

      final response = await _model.generateContent([
        Content.multi([prompt, imagePart])
      ]);

      return response.text ?? 'Yapay zekadan bir yanıt alınamadı. Lütfen tekrar deneyin.';
    } catch (e) {
      return 'Hata oluştu: $e';
    }
  }
}
