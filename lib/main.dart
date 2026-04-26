import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart'; // .env için gerekli
import 'login_screen.dart'; // Giriş ekranın

void main() async {
  // Uygulama başlamadan önce gerekli ayarları yapıyoruz
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // API anahtarı için .env dosyasını yüklüyoruz
    await dotenv.load(fileName: ".env");
  } catch (e) {
    debugPrint(".env dosyası yüklenemedi, lütfen kontrol et: $e");
  }

  runApp(const MedikalTercumanApp());
}

class MedikalTercumanApp extends StatelessWidget {
  const MedikalTercumanApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Medikal Rapor Tercümanı',
      debugShowCheckedModeBanner: false, // Sağ üstteki debug yazısını kaldırır
      theme: ThemeData(
        // Sağlık temasına uygun ana renk paleti
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue.shade700),
        useMaterial3: true,
        // Genel metin stillerini buradan da yönetebilirsin
        fontFamily: 'Inter',
      ),
      // Uygulama artık her zaman Giriş Ekranı ile başlayacak
      home: const LoginScreen(),
    );
  }
}
