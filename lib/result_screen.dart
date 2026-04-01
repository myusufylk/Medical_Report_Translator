import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'services/gemini_service.dart';

class ResultScreen extends StatefulWidget {
  final Uint8List imageBytes;
  final String reportType;

  const ResultScreen({
    super.key,
    required this.imageBytes,
    required this.reportType,
  });

  @override
  State<ResultScreen> createState() => _ResultScreenState();
}

class _ResultScreenState extends State<ResultScreen> {
  final GeminiService _geminiService = GeminiService();
  String? _resultText;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _analyzeReport();
  }

  Future<void> _analyzeReport() async {
    try {
      final result = await _geminiService.analyzeReport(
        widget.imageBytes,
        widget.reportType,
      );
      if (mounted) {
        setState(() {
          _resultText = result;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _resultText = 'Beklenmeyen bir hata oluştu:\\n$e';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Rapor Çeviri Sonucu'),
        centerTitle: true,
        backgroundColor: Colors.blue.shade50,
      ),
      body: _isLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 20),
                  Text(
                    'Raporunuz yapay zeka ile analiz ediliyor...',
                    style: TextStyle(fontSize: 16, color: Colors.black54),
                  ),
                  SizedBox(height: 10),
                  Text(
                    'Lütfen bekleyin',
                    style: TextStyle(fontSize: 14, color: Colors.blue),
                  ),
                ],
              ),
            )
          : Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  // Rapor Önizleme Alanı
                  Container(
                    height: 150,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.shade100, width: 2),
                      image: DecorationImage(
                        image: MemoryImage(widget.imageBytes),
                        fit: BoxFit.cover,
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Row(
                    children: [
                      Icon(Icons.auto_awesome, color: Colors.amber),
                      SizedBox(width: 10),
                      Text(
                        'AI Çevirisi',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const Divider(),
                  const SizedBox(height: 10),
                  // Markdown çıktısı için formatlanmış metin alanı
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: Colors.blue.shade50.withOpacity(0.5),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Markdown(
                        data: _resultText ?? '',
                        styleSheet: MarkdownStyleSheet(
                          p: const TextStyle(fontSize: 16, height: 1.5),
                          h1: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                          h2: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                          listBullet: const TextStyle(fontSize: 16),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.popUntil(context, (route) => route.isFirst);
                      },
                      icon: const Icon(Icons.home, color: Colors.white),
                      label: const Text(
                        'Yeni Rapor Çevir (Ana Menü)',
                        style: TextStyle(fontSize: 16, color: Colors.white),
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
            ),
    );
  }
}
