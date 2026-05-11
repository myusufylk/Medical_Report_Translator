import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart'; // MediaType için gerekli
import '../report_model.dart';

class ApiService {
  // Ana URL
  static const String baseUrl =
      'https://medical-report-translator-1.onrender.com';

  // 1. Yeni Raporu Analize Gönder
  // isPdf parametresini ekledik, varsayılan olarak false (resim) kabul ediyoruz
  Future<MedicalReport> uploadReport(
    File imageFile,
    String type, {
    bool isPdf = false,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/ocr-new'),
      );

      // Backend'in beklediği ek alanlar
      request.fields['report_type'] = type;

      // Dosya gönderimi - Dosya tipini (MediaType) dinamik olarak belirliyoruz
      request.files.add(
        await http.MultipartFile.fromPath(
          'file',
          imageFile.path,
          // PDF ise 'application/pdf', değilse 'image/jpeg' olarak işaretliyoruz
          contentType:
              isPdf
                  ? MediaType('application', 'pdf')
                  : MediaType('image', 'jpeg'),
        ),
      );

      // İsteği gönder ve yanıtı al
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        return MedicalReport.fromJson(json.decode(response.body));
      } else {
        // Hata detayını konsola yazdır (400/500 hatalarını yakalamak için)
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
        List data = json.decode(response.body);
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
