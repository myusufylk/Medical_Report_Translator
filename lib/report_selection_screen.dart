import 'package:flutter/material.dart';

class ReportSelectionScreen extends StatelessWidget {
  const ReportSelectionScreen({super.key});

  // Tıklanan rapor türü için alt menü (Kamera/PDF seçimi) açan fonksiyon
  void _showUploadOptions(BuildContext context, String reportType) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '$reportType Yükle',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              ListTile(
                leading: const Icon(
                  Icons.camera_alt,
                  color: Colors.blue,
                  size: 30,
                ),
                title: const Text('Kamerayla Çek'),
                onTap: () {
                  // TODO: İleride kamerayı açacak kod buraya gelecek
                  Navigator.pop(context);
                },
              ),
              ListTile(
                leading: const Icon(
                  Icons.picture_as_pdf,
                  color: Colors.red,
                  size: 30,
                ),
                title: const Text('PDF veya Görsel Seç'),
                onTap: () {
                  // TODO: İleride galeriyi/dosyaları açacak kod buraya gelecek
                  Navigator.pop(context);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blue.shade50,
      appBar: AppBar(
        title: const Text('Rapor Türünü Seçin'),
        centerTitle: true,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 10),
              child: Text(
                'Lütfen tercüme etmek istediğiniz belgenin türünü seçin:',
                style: TextStyle(fontSize: 16, color: Colors.black87),
              ),
            ),
            const SizedBox(height: 10),

            // 1. Seçenek: Kan Tahlili
            _buildReportCard(
              context,
              title: 'Kan Tahlili',
              subtitle: 'Hemogram (Tam Kan) ve Rutin Biyokimya',
              icon: Icons.bloodtype,
              color: Colors.red.shade400,
            ),

            // 2. Seçenek: Epikriz Raporu
            _buildReportCard(
              context,
              title: 'Epikriz Raporu',
              subtitle: 'Hastane taburcu ve durum özetleri',
              icon: Icons.description,
              color: Colors.blue.shade600,
            ),

            // 3. Seçenek: EKG Raporu
            _buildReportCard(
              context,
              title: 'EKG Metin Raporu',
              subtitle: 'Cihazın verdiği yazılı ritim analizleri',
              icon: Icons.monitor_heart,
              color: Colors.green.shade600,
            ),
          ],
        ),
      ),
    );
  }

  // Tasarımı temiz tutmak için kartları oluşturan yardımcı bir widget
  Widget _buildReportCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      child: InkWell(
        onTap: () => _showUploadOptions(context, title),
        borderRadius: BorderRadius.circular(15),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, size: 32, color: color),
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios,
                color: Colors.grey.shade400,
                size: 20,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
