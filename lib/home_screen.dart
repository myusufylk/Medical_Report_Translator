import 'package:flutter/material.dart';
import 'report_selection_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FBFF),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 30),
              // 1. Üst Alan: Karşılama ve Profil
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Merhaba,',
                        style: TextStyle(
                          fontSize: 18,
                          color: Colors.blue.shade800,
                        ),
                      ),
                      const Text(
                        'Sağlıklı Günler!',
                        style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF2C3E50),
                        ),
                      ),
                    ],
                  ),
                  _buildProfileIcon(),
                ],
              ),
              const SizedBox(height: 32),

              // 2. Ana Aksiyon Kartı: Yeni Rapor Analizi
              _buildMainActionCard(context),
              const SizedBox(height: 40),

              // 3. Geçmiş Raporlarım Sekmesi (Hızlı İşlemler kaldırıldı)
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Geçmiş Raporlarım',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2C3E50),
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      // Tüm geçmişi görme sayfasına yönlendirme
                    },
                    child: Text(
                      'Tümünü Gör',
                      style: TextStyle(color: Colors.blue.shade700),
                    ),
                  ),
                ],
              ),
              _buildEmptyHistoryCard(),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }

  // Profil İkonu Tasarımı
  Widget _buildProfileIcon() {
    return Container(
      padding: const EdgeInsets.all(2),
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: Colors.blue.shade100, width: 2),
      ),
      child: CircleAvatar(
        radius: 25,
        backgroundColor: Colors.white,
        child: Icon(
          Icons.person_outline,
          color: Colors.blue.shade700,
          size: 30,
        ),
      ),
    );
  }

  // Ana Rapor Analiz Kartı
  Widget _buildMainActionCard(BuildContext context) {
    return GestureDetector(
      onTap:
          () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const ReportSelectionScreen(),
            ),
          ),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.blue.shade700, Colors.blue.shade500],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.blue.withOpacity(0.3),
              blurRadius: 15,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.analytics_outlined,
                color: Colors.white,
                size: 30,
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Yeni Rapor Analiz Et',
              style: TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Tahlillerinizi yapay zeka ile halk diline çevirin.',
              style: TextStyle(
                color: Colors.white.withOpacity(0.9),
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Boş Geçmiş Kartı
  Widget _buildEmptyHistoryCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade100),
      ),
      child: Column(
        children: [
          Icon(Icons.history_toggle_off, color: Colors.grey.shade300, size: 60),
          const SizedBox(height: 16),
          Text(
            'Henüz analiz edilmiş bir raporunuz yok.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey.shade500, fontSize: 14),
          ),
        ],
      ),
    );
  }
}
