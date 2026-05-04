import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_tts/flutter_tts.dart'; // TTS için
import 'package:pdf/pdf.dart'; // PDF için
import 'package:pdf/widgets.dart' as pw; // PDF Tasarımı için
import 'package:printing/printing.dart'; // PDF Paylaşımı için

class ResultScreen extends StatefulWidget {
  final Uint8List fileBytes;
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

  // TTS ve PDF için değişkenler
  final FlutterTts _flutterTts = FlutterTts();
  bool _isSpeaking = false;

  @override
  void initState() {
    super.initState();
    _initTts();
    _analyzeReport();
  }

  // 1. TTS (Sesli Okuma) Başlatma
  void _initTts() {
    _flutterTts.setLanguage("tr-TR"); // Türkçe dili ayarla
    _flutterTts.setPitch(1.0);
    _flutterTts.setSpeechRate(0.5); // Okuma hızı

    _flutterTts.setStartHandler(() => setState(() => _isSpeaking = true));
    _flutterTts.setCompletionHandler(() => setState(() => _isSpeaking = false));
    _flutterTts.setErrorHandler((msg) => setState(() => _isSpeaking = false));
  }

  // 2. Sesli Oku Fonksiyonu
  Future<void> _speak() async {
    if (_isSpeaking) {
      await _flutterTts.stop();
      setState(() => _isSpeaking = false);
    } else {
      if (_translatedText.isNotEmpty) {
        // Markdown karakterlerini temizleyip düz metni okutuyoruz
        String plainText = _translatedText.replaceAll(RegExp(r'[*#-]'), '');
        await _flutterTts.speak(plainText);
      }
    }
  }

  // 3. PDF Olarak Dışa Aktar/Paylaş
  Future<void> _exportPdf() async {
    final pdf = pw.Document();

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        build: (pw.Context context) {
          return pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Text(
                "Tıbbi Rapor Analizi",
                style: pw.TextStyle(
                  fontSize: 22,
                  fontWeight: pw.FontWeight.bold,
                ),
              ),
              pw.Divider(),
              pw.SizedBox(height: 10),
              pw.Text("Rapor Türü: ${widget.reportType}"),
              pw.SizedBox(height: 20),
              pw.Text(
                "Analiz Özeti:",
                style: pw.TextStyle(fontWeight: pw.FontWeight.bold),
              ),
              pw.SizedBox(height: 10),
              pw.Text(
                _translatedText.replaceAll(RegExp(r'[*#]'), ''),
              ), // Markdown sembollerinden arındırılmış metin
              pw.SizedBox(height: 30),
              pw.Divider(),
              pw.Text(
                "Not: Bu analiz yapay zeka tarafından asistanlık amacıyla üretilmiştir. Lütfen doktorunuza danışın.",
                style: const pw.TextStyle(fontSize: 10),
              ),
            ],
          );
        },
      ),
    );

    await Printing.sharePdf(
      bytes: await pdf.save(),
      filename: 'rapor_analizi.pdf',
    );
  }

  Future<void> _analyzeReport() async {
    await Future.delayed(const Duration(seconds: 3));

    if (mounted) {
      setState(() {
        _isLoading = false;
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
  void dispose() {
    _flutterTts.stop(); // Sayfadan çıkınca sesi durdur
    super.dispose();
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
        actions: [
          if (!_isLoading)
            IconButton(
              icon: const Icon(Icons.share, color: Colors.blue),
              onPressed: _exportPdf,
            ),
        ],
      ),
      body: _isLoading ? _buildLoadingView() : _buildResultView(),
    );
  }

  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
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
        ],
      ),
    );
  }

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
                    // withOpacity yerine yeni standart withValues kullanıldı
                    color: Colors.black.withValues(alpha: 0.05),
                    blurRadius: 10,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: SingleChildScrollView(
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
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _speak,
                  icon: Icon(
                    _isSpeaking ? Icons.stop : Icons.volume_up,
                    color: Colors.white,
                  ),
                  label: Text(
                    _isSpeaking ? 'Durdur' : 'Sesli Oku',
                    style: const TextStyle(color: Colors.white),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange.shade700,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _exportPdf,
                  icon: const Icon(Icons.picture_as_pdf, color: Colors.white),
                  label: const Text(
                    'PDF Paylaş',
                    style: TextStyle(color: Colors.white),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade700,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            height: 50,
            child: ElevatedButton.icon(
              onPressed: () => Navigator.pop(context),
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
