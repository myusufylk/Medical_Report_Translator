import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart'; // MediaType için gerekli
import '../report_model.dart';

class ApiService {
  // 🚀 Başındaki ve içindeki tüm görünmez boşluklar tamamen temizlendi:
  static const String baseUrl = 'https://jersey-booted-salami.ngrok-free.dev';

  // 1. Yeni Raporu Analize Gönder
  Future<MedicalReport> uploadReport(
    Uint8List fileBytes,
    String type, {
    bool isPdf = false,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/ocr-new'),
      );

      // Backend'in (main.py) beklediği tam parametre adı: report_type
      // Sistemde "Kan Tahlili" seçildiyse arka planda "Biyokimya" sözlüğüyle eşleşmesi için düzeltiyoruz
      String backendType = type;
      if (type == "Kan Tahlili") {
        backendType = "Biyokimya";
      }
      request.fields['report_type'] = backendType;

      // Dosya uzantısını ve içerik tipini belirliyoruz
      String fileName = isPdf ? 'report.pdf' : 'report.jpg';
      MediaType mediaType =
          isPdf ? MediaType('application', 'pdf') : MediaType('image', 'jpeg');

      // Dosya gönderimi - Saf byte'lar ile form-data yüklemesi
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          fileBytes,
          filename: fileName,
          contentType: mediaType,
        ),
      );

      // İsteği gönder ve yanıtı al
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final Map<String, dynamic> responseData = json.decode(
          utf8.decode(response.bodyBytes),
        );

        // Backend'den gelen iki ana çıktıyı (islenmis_veri ve analiz)
        // MarkdownBody'nin mükemmel görüntüleyebileceği tek bir gövdede birleştiriyoruz
        String mergedMarkdown = "";

        if (responseData.containsKey('islenmis_veri') &&
            responseData['islenmis_veri'].toString().isNotEmpty) {
          mergedMarkdown +=
              "### 📋 Ayıklanan Değerler ve Durum\n\n${responseData['islenmis_veri']}\n\n---\n\n";
        }

        if (responseData.containsKey('analiz') &&
            responseData['analiz'].toString().isNotEmpty) {
          mergedMarkdown +=
              "### 🩺 Yapay Zeka Hekim Analizi\n\n${responseData['analiz']}";
        }

        // Eğer iki veri de boş geldiyse emniyet kilidi
        if (mergedMarkdown.isEmpty) {
          mergedMarkdown =
              "Rapor başarıyla okundu ancak anlamlı bir analiz üretilemedi.";
        }

        // Arayüzün (report_model.dart) beklediği json haritasını simüle ediyoruz
        Map<String, dynamic> adaptedJson = {
          "id": DateTime.now().millisecondsSinceEpoch.toString(),
          "created_at": "Şimdi Analiz Edildi",
          "report_type": type,
          "report_name": fileName,
          "summary_text":
              mergedMarkdown, // Birleştirilmiş Markdown buraya oturuyor
          "status": "Success",
        };

        return MedicalReport.fromJson(adaptedJson);
      } else {
        print("****************************************");
        print("SUNUCU HATASI (${response.statusCode}): ${response.body}");
        print("****************************************");

        throw Exception(
          'Sunucu Hatası: ${response.statusCode}\nDetay: ${response.body}',
        );
      }
    } catch (e) {
      print("API SERVICE ERROR: $e");
      throw Exception('İşlem sırasında hata oluştu: $e');
    }
  }

  // 2. Geçmiş Raporları Getir
  Future<List<MedicalReport>> getHistory() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/history'));

      if (response.statusCode == 200) {
        List data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((json) => MedicalReport.fromJson(json)).toList();
      } else {
        print("GEÇMİŞ ÇEKME HATASI: ${response.body}");
        throw Exception('Geçmiş yüklenemedi: ${response.statusCode}');
      }
    } catch (e) {
      print("Kritik Hata: $e");
      throw Exception('Sunucuya bağlanılamadı: $e');
    }
  }
}
