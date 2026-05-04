import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:path_provider/path_provider.dart';
import 'report_model.dart';
import 'services/api_service.dart';

class ResultScreen extends StatefulWidget {
  final MedicalReport? report;
  final Uint8List? fileBytes;
  final String? reportType;

  const ResultScreen({super.key, this.report, this.fileBytes, this.reportType});

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  bool _isLoading = false;
  late MedicalReport _currentReport;

  @override
  void initState() {
    super.initState();
    if (widget.report != null) {
      _currentReport = widget.report!;
      _isLoading = false;
    } else {
      _isLoading = true;
      _analyzeReport();
    }
  }

  Future<void> _analyzeReport() async {
    try {
      // 1. Dosya türünü baytlardan anla (PDF imzası: %PDF)
      final bool isPdf =
          widget.fileBytes!.length > 4 &&
          widget.fileBytes![0] == 0x25 &&
          widget.fileBytes![1] == 0x50 &&
          widget.fileBytes![2] == 0x44 &&
          widget.fileBytes![3] == 0x46;

      final String extension = isPdf ? "pdf" : "jpg";

      // 2. Geçici dizini al ve doğru uzantıyla dosyayı oluştur
      final tempDir = await getTemporaryDirectory();
      final tempFile = File('${tempDir.path}/temp_report.$extension');

      // 3. Bayt verisini dosyaya yaz
      await tempFile.writeAsBytes(widget.fileBytes!);

      // 4. API servisini çağır (isPdf parametresini gönderiyoruz)
      final response = await ApiService().uploadReport(
        tempFile,
        widget.reportType ?? "Genel Analiz",
        isPdf: isPdf, // ApiService tarafında bu kontrolü eklemiştik
      );

      if (mounted) {
        setState(() {
          _isLoading = false;
          _currentReport = response;
        });
      }
    } catch (e, stacktrace) {
      print("****************************************");
      print("HATA OLUŞTU: $e");
      print("HATA KAYNAĞI: $stacktrace");
      print("****************************************");

      if (mounted) {
        setState(() {
          _isLoading = false;
          _currentReport = MedicalReport(
            id: "error",
            date: "Hata",
            reportType: "Hata",
            reportName: "Hata",
            aiResponse:
                "### ⚠️ Analiz Hatası\n\nSunucu dosyayı işleyemedi. Lütfen dosyanın bozuk olmadığından emin olun veya Render sunucusunun uyanmasını bekleyin.\n\n**Hata Detayı:** $e",
            status: "Hata",
          );
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F7FF),
      appBar: AppBar(
        title: const Text(
          'Analiz Sonucu',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: _isLoading ? _buildLoadingView() : _buildResultView(),
    );
  }

  Widget _buildLoadingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 80,
            height: 80,
            child: CircularProgressIndicator(
              color: Colors.blue.shade700,
              strokeWidth: 6,
            ),
          ),
          const SizedBox(height: 30),
          const Text(
            'Raporunuz Analiz Ediliyor...',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          const Text('İlk istekte sunucunun uyanması 1 dk sürebilir.'),
        ],
      ),
    );
  }

  Widget _buildResultView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildModernResultCard(_currentReport),
          const SizedBox(height: 20),
          _buildActionButtons(),
        ],
      ),
    );
  }

  Widget _buildModernResultCard(MedicalReport report) {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withValues(alpha: 0.08),
            blurRadius: 20,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(24),
                topRight: Radius.circular(24),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  report.date,
                  style: TextStyle(
                    color: Colors.blue.shade800,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Icon(Icons.auto_awesome, color: Colors.blue, size: 20),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(20.0),
            child: MarkdownBody(
              data: report.aiResponse,
              styleSheet: MarkdownStyleSheet(
                p: const TextStyle(
                  fontSize: 15,
                  height: 1.6,
                  color: Colors.black87,
                ),
                h3: TextStyle(
                  color: Colors.blue.shade900,
                  fontWeight: FontWeight.bold,
                ),
                listBullet: const TextStyle(color: Colors.blue),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return SizedBox(
      width: double.infinity,
      height: 55,
      child: ElevatedButton.icon(
        onPressed: () => Navigator.pop(context),
        icon: const Icon(Icons.check_circle, color: Colors.white),
        label: const Text(
          'Anladım, Kapat',
          style: TextStyle(color: Colors.white, fontSize: 16),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.blue.shade700,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
        ),
      ),
    );
  }
}
