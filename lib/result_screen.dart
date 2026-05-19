import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_tts/flutter_tts.dart'; // TTS Kütüphanesi geri geldi
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
  MedicalReport? _currentReport;

  // TTS Durum Yönetimi
  final FlutterTts _flutterTts = FlutterTts();
  bool _isSpeaking = false;

  @override
  void initState() {
    super.initState();
    _initTts(); // TTS Ayarlarını yükle
    if (widget.report != null) {
      _currentReport = widget.report;
      _isLoading = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _showResultModal(context, _currentReport!);
      });
    } else {
      _isLoading = true;
      _analyzeReport();
    }
  }

  // TTS Ayarları (Türkçe ve İdeal Hız)
  void _initTts() async {
    await _flutterTts.setLanguage("tr-TR");
    await _flutterTts.setSpeechRate(0.5);
    await _flutterTts.setVolume(1.0);

    _flutterTts.setStartHandler(() {
      if (mounted) setState(() => _isSpeaking = true);
    });

    _flutterTts.setCompletionHandler(() {
      if (mounted) setState(() => _isSpeaking = false);
    });

    _flutterTts.setErrorHandler((msg) {
      if (mounted) setState(() => _isSpeaking = false);
    });
  }

  // Seslendirmeyi Başlat / Durdur
  void _toggleSpeech(String text) async {
    if (_isSpeaking) {
      await _flutterTts.stop();
      if (mounted) setState(() => _isSpeaking = false);
    } else {
      if (text.isNotEmpty) {
        // Markdown gürültülerini temizleme filtresi
        String cleanText = text
            .replaceAll('#', '')
            .replaceAll('*', '')
            .replaceAll('-', '')
            .replaceAll('⚠️', '')
            .replaceAll('⬆️', '')
            .replaceAll('⬇️', '')
            .replaceAll('✅', '');
        await _flutterTts.speak(cleanText);
      }
    }
  }

  Future<void> _analyzeReport() async {
    try {
      final bool isPdf =
          widget.fileBytes!.length > 4 &&
          widget.fileBytes![0] == 0x25 &&
          widget.fileBytes![1] == 0x50 &&
          widget.fileBytes![2] == 0x44 &&
          widget.fileBytes![3] == 0x46;

      final response = await ApiService().uploadReport(
        widget.fileBytes!,
        widget.reportType ?? "Genel Analiz",
        isPdf: isPdf,
      );

      if (mounted) {
        setState(() {
          _isLoading = false;
          _currentReport = response;
        });
        _showResultModal(context, _currentReport!);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _currentReport = MedicalReport(
            id: "error",
            date: "Hata",
            reportType: "Hata",
            reportName: "Hata",
            aiResponse:
                "### ⚠️ Analiz Hatası\n\nSunucu dosyayı işleyemedi. Lütfen internet bağlantınızı veya backend durumunu kontrol edin.\n\n**Detay:** $e",
            status: "Hata",
          );
        });
        _showResultModal(context, _currentReport!);
      }
    }
  }

  @override
  void dispose() {
    _flutterTts.stop(); // Sayfa kapanınca sesi kes
    super.dispose();
  }

  // Cemre'nin Tasarladığı Modern Alttan Açılan Pencere (StatefulBuilder ile TTS uyumlu yapıldı)
  void _showResultModal(BuildContext context, MedicalReport report) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return StatefulBuilder(
          builder: (BuildContext context, StateSetter modalState) {
            // Ana ekran ile modal arasındaki ses senkronizasyonunu kuruyoruz
            _flutterTts.setStartHandler(() {
              if (mounted) {
                setState(() => _isSpeaking = true);
                modalState(() {});
              }
            });
            _flutterTts.setCompletionHandler(() {
              if (mounted) {
                setState(() => _isSpeaking = false);
                modalState(() {});
              }
            });

            return Container(
              height: MediaQuery.of(context).size.height * 0.85,
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(30),
                  topRight: Radius.circular(30),
                ),
              ),
              child: Column(
                children: [
                  // Üst Tutamaç Çubuğu
                  const SizedBox(height: 12),
                  Container(
                    width: 50,
                    height: 5,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Başlık Alanı ve Sağ Köşede Modern TTS Butonu
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.blue.shade50,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Icon(
                                Icons.auto_awesome,
                                color: Colors.blue.shade700,
                                size: 24,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Yapay Zeka Analizi',
                              style: TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                                color: Colors.blue.shade900,
                              ),
                            ),
                          ],
                        ),
                        // 🔊 SESLENDİRME BUTONU (Tasarım harikası oldu)
                        IconButton(
                          onPressed: () {
                            _toggleSpeech(report.aiResponse);
                            modalState(
                              () {},
                            ); // Sadece modal ekranını günceller
                          },
                          icon: AnimatedSwitcher(
                            duration: const Duration(milliseconds: 300),
                            child: Icon(
                              _isSpeaking ? Icons.volume_up : Icons.volume_mute,
                              key: ValueKey<bool>(_isSpeaking),
                              color:
                                  _isSpeaking
                                      ? Colors.green.shade600
                                      : Colors.blue.shade700,
                              size: 28,
                            ),
                          ),
                          tooltip: _isSpeaking ? "Sesi Durdur" : "Sesli Dinle",
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Rapor İçeriği (Markdown)
                  Expanded(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
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
                            height: 2.0,
                          ),
                          listBullet: const TextStyle(
                            color: Colors.blue,
                            fontSize: 16,
                          ),
                        ),
                      ),
                    ),
                  ),

                  // Kapat Butonu
                  Padding(
                    padding: const EdgeInsets.all(24),
                    child: SizedBox(
                      width: double.infinity,
                      height: 55,
                      child: ElevatedButton(
                        onPressed: () {
                          _flutterTts.stop(); // Kapatınca sesi sustur
                          Navigator.pop(context); // Modalı kapat
                          Navigator.pop(context); // Bir önceki ekrana dön
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue.shade700,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                          elevation: 0,
                        ),
                        child: const Text(
                          'Kapat',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    ).then((_) {
      _flutterTts
          .stop(); // Kullanıcı dışarı tıklayıp modalı kapatırsa yine sesi durdur
    });
  }

  @override
  Widget build(BuildContext context) {
    // Arka plandaki modern, degrade (gradient) geçişli yükleme ekranı
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFE0F2FE), Color(0xFFF8FAFC)],
          ),
        ),
        child:
            _isLoading
                ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      CircularProgressIndicator(
                        color: Colors.blue.shade700,
                        strokeWidth: 5,
                      ),
                      const SizedBox(height: 24),
                      Text(
                        'Raporunuz İnceleniyor...',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue.shade900,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Yapay zeka verileri ayrıştırıyor.',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.blue.shade700,
                        ),
                      ),
                    ],
                  ),
                )
                : const SizedBox.shrink(),
      ),
    );
  }
}
