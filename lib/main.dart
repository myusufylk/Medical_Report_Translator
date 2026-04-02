import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'report_selection_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  runApp(const MedikalTercumanApp());
}

class MedikalTercumanApp extends StatelessWidget {
  const MedikalTercumanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Medikal Tercüman',
      debugShowCheckedModeBanner:
          false, // Sağ üstteki çirkin 'Debug' etiketini kaldırır
      theme: ThemeData(
        // Sağlık uygulamasına yakışacak güven veren bir mavi tonu
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue.shade700),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text(
          'Medikal Rapor Tercümanı',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.blue.shade50,
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Temsili Logo / İkon
              Icon(
                Icons.medical_information,
                size: 100,
                color: Colors.blue.shade700,
              ),
              const SizedBox(height: 30),

              const Text(
                'Hoş Geldiniz',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 15),

              const Text(
                'Karmaşık tahlil ve epikriz raporlarınızı saniyeler içinde herkesin anlayabileceği günlük dile çevirin.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.black54,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 50),

              // Ana Aksiyon Butonu
              SizedBox(
                width: double.infinity, // Butonu ekranın genişliğine yayar
                height: 55,
                child: ElevatedButton.icon(
                  onPressed: () {
                    // 2. Ekrana (Rapor Seçimi) Geçiş Kodu
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ReportSelectionScreen(),
                      ),
                    );
                  },
                  icon: const Icon(Icons.document_scanner, color: Colors.white),
                  label: const Text(
                    'Yeni Rapor Çevir',
                    style: TextStyle(fontSize: 18, color: Colors.white),
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
      ),
    );
  }
}
