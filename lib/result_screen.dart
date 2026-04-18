import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class ResultScreen extends StatefulWidget {
  final Uint8List fileBytes; // Artık sadece resim değil, PDF de gelebilir
  final String reportType;

  const ResultScreen({
    super.key,
    required this.fileBytes,
    required this.reportType,
  });

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _isLoading = true;
  String _translatedText = "";

  @override
  void initState() {
    super.initState();
    _analyzeReport();
  }

  // Yapay zeka sürecini simüle eden fonksiyon
  Future<void> _analyzeReport() async {
    // Sprint 3'te buraya Gemini veya Kendi Modelimizin API isteği gelecek.
    // Şimdilik 3 saniyelik bir yükleme süresi simüle ediyoruz.
    await Future.delayed(const Duration(seconds: 3));

    if (mounted) {
      setState(() {
        _isLoading = false;
        // Yapay zekadan dönecek olan Markdown formatlı örnek metin:
        _translatedText = """
### 📋 Rapor Özeti: ${widget.reportType}

Merhaba, raporunuzu inceledim. Tıbbi terimleri sizin için basitleştirdim:

* **Lökosit (WBC):** Değerleriniz normal sınırların biraz üzerinde. Bu, vücudunuzun ufak bir enfeksiyonla savaştığı anlamına gelebilir.
* **Hemoglobin (HGB):** Kanınızdaki oksijen taşıyan hücrelerin seviyesi gayet sağlıklı bir aralıkta.

**💡 Önemli Not:** *Ben bir yapay zekâ asistanıyım, teşhis koyamam. Lütfen bu sonuçları kesinlikle kendi doktorunuzla da paylaşın.*
""";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      appBar: AppBar(
        title: const Text('Analiz Sonucu'),
        centerTitle: true,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: _isLoading ? _buildLoadingView() : _buildResultView(),
    );
  }

  // 1. EKRAN: YÜKLENİYOR ANİMASYONU
  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Sağlık temasına uygun dönen bir yükleme ikonu
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 80,
                height: 80,
                child: CircularProgressIndicator(
                  color: Colors.blue.shade700,
                  strokeWidth: 6,
                ),
              ),
              Icon(
                Icons.medical_services,
                color: Colors.blue.shade700,
                size: 35,
              ),
            ],
          ),
          const SizedBox(height: 30),
          const Text(
            'Raporunuz analiz ediliyor...',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          Text(
            'Tıbbi terimler halk diline çevriliyor\nLütfen bekleyin.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: Colors.grey.shade600),
          ),
        ],
      ),
    );
  }

  // 2. EKRAN: SONUÇ GÖSTERİMİ
  Widget _buildResultView() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Expanded(
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(15),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    spreadRadius: 2,
                  ),
                ],
              ),
              // Markdown paketi sayesinde yapay zeka çıktısı kalın, italik ve listeler halinde şıkça görünür.
              child: MarkdownBody(
                data: _translatedText,
                styleSheet: MarkdownStyleSheet(
                  h3: TextStyle(
                    color: Colors.blue.shade800,
                    fontWeight: FontWeight.bold,
                  ),
                  p: const TextStyle(fontSize: 16, height: 1.5),
                  listBullet: TextStyle(color: Colors.blue.shade600),
                ),
              ),
            ),
          ),
          const SizedBox(height: 20),
          // Gelecekte eklenecek olan "Sesli Oku" veya "PDF Olarak İndir" butonları için alan
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.pop(context); // Ana menüye veya rapor seçimine dön
              },
              icon: const Icon(Icons.check_circle, color: Colors.white),
              label: const Text(
                'Tamamla',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue.shade700,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
