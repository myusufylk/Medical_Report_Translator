import 'package:flutter/material.dart';
import 'home_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FBFF),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 30.0),
            child: Column(
              children: [
                const SizedBox(height: 50),

                // 1. Üstteki Logo Bölümü
                Center(
                  child: Container(
                    width: 240,
                    height: 140,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(30),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.blue.withOpacity(0.09),
                          blurRadius: 22,
                          spreadRadius: 4,
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(30),
                      child: Image.asset(
                        'assets/login_logo.png',
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) {
                          return Container(
                            color: Colors.blue.shade50,
                            child: Center(
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.image_not_supported,
                                    size: 36,
                                    color: Colors.blue.shade200,
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Logo yüklenemedi',
                                    style: TextStyle(
                                      color: Colors.blue.shade300,
                                      fontSize: 14,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                const Text(
                  'Fırat Üniversitesi',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF2C3E50),
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Tıbbi Rapor Tercümanı',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFF4F5D75),
                    letterSpacing: 0.6,
                  ),
                ),
                const SizedBox(height: 40),

                // 2. Giriş Alanları
                _buildModernTextField(
                  label: 'T.C. Kimlik Numarası',
                  icon: Icons.badge_outlined,
                  keyboardType: TextInputType.number,
                ),
                const SizedBox(height: 20),
                _buildModernTextField(
                  label: 'Şifre',
                  icon: Icons.lock_open_outlined,
                  isPassword: true,
                ),
                const SizedBox(height: 40),

                // 3. Aksiyon Butonları
                // GİRİŞ YAP (Ana Renk)
                _buildActionButton(
                  text: 'Giriş Yap',
                  color: Colors.blue.shade700,
                  onPressed: () {
                    Navigator.pushReplacement(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const HomeScreen(),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 12),

                // KAYIT OL (Vurgulu Kenarlık veya Farklı Ton)
                _buildActionButton(
                  text: 'Kayıt Ol',
                  color: Colors.white,
                  textColor: Colors.blue.shade700,
                  isOutlined: true,
                  onPressed: () {
                    // Kayıt olma ekranına yönlendirme buraya gelecek
                  },
                ),
                const SizedBox(height: 12),

                // ŞİFREMİ UNUTTUM (Gri/Sade)
                _buildActionButton(
                  text: 'Şifremi Unuttum',
                  color: Colors.grey.shade300,
                  textColor: Colors.black54,
                  onPressed: () {
                    // Şifre sıfırlama işlemi
                  },
                ),
                const SizedBox(height: 30),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Modern Input Tasarımı
  Widget _buildModernTextField({
    required String label,
    required IconData icon,
    bool isPassword = false,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(15),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: TextField(
        obscureText: isPassword,
        keyboardType: keyboardType,
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: Icon(icon, color: Colors.blue.shade300),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(15),
            borderSide: BorderSide.none,
          ),
          filled: true,
          fillColor: Colors.white,
          labelStyle: const TextStyle(color: Colors.grey),
        ),
      ),
    );
  }

  // Modern Buton Tasarımı
  Widget _buildActionButton({
    required String text,
    required Color color,
    required VoidCallback onPressed,
    Color textColor = Colors.white,
    bool isOutlined = false,
  }) {
    return SizedBox(
      width: double.infinity,
      height: 55,
      child: ElevatedButton(
        onPressed: onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: color,
          elevation: isOutlined ? 0 : 2,
          side:
              isOutlined
                  ? BorderSide(color: Colors.blue.shade700, width: 2)
                  : BorderSide.none,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(15),
          ),
        ),
        child: Text(
          text,
          style: TextStyle(
            color: textColor,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
