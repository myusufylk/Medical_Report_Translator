import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'result_screen.dart';

class ReportSelectionScreen extends StatelessWidget {
  const ReportSelectionScreen({super.key});

  Future<void> _pickFile(BuildContext context, String reportType) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: [
          'jpg',
          'jpeg',
          'png',
          'gif',
        ], // Geçici olarak sadece resimler
        allowMultiple: false,
        withData: true, // Web'de bytes almak için zorunlu
      );

      if (context.mounted && result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        if (file.bytes != null) {
          Navigator.pop(context); // Selection modalını kapat
          Navigator.push(
            context,
            MaterialPageRoute(
              builder:
                  (context) => ResultScreen(
                    fileBytes: file.bytes!,
                    reportType: reportType,
                  ),
            ),
          );
        } else {
          _showError(context, 'Dosya okunamadı (boş veya geçersiz format).');
        }
      }
    } catch (e) {
      if (context.mounted) {
        _showError(context, 'Dosya seçilirken hata oluştu: $e');
      }
    }
  }

  Future<void> _takePhoto(BuildContext context, String reportType) async {
    try {
      final ImagePicker picker = ImagePicker();
      final XFile? photo = await picker.pickImage(
        source: ImageSource.camera,
        imageQuality: 85,
      );

      if (context.mounted && photo != null) {
        final Uint8List imageBytes = await photo.readAsBytes();
        Navigator.pop(context); // Modal kapat
        Navigator.push(
          context,
          MaterialPageRoute(
            builder:
                (context) =>
                    ResultScreen(fileBytes: imageBytes, reportType: reportType),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        _showError(context, 'Kamera açılırken hata oluştu: $e');
      }
    }
  }

  void _showError(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
        duration: const Duration(seconds: 3),
      ),
    );
  }

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
                onTap: () => _takePhoto(context, reportType),
              ),
              ListTile(
                leading: const Icon(Icons.image, color: Colors.red, size: 30),
                title: const Text('Galeriden Görsel Seç'),
                onTap: () => _pickFile(context, reportType),
              ),
              // PDF Seçeneği Buraya Eklendi
              ListTile(
                leading: const Icon(
                  Icons.picture_as_pdf,
                  color: Colors.orange,
                  size: 30,
                ),
                title: const Text('Cihazdan PDF Seç'),
                onTap: () => _pickPDF(context, reportType),
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

            _buildReportCard(
              context,
              title: 'Kan Tahlili',
              subtitle: 'Hemogram (Tam Kan) ve Rutin Biyokimya',
              icon: Icons.bloodtype,
              color: Colors.red.shade400,
            ),
            _buildReportCard(
              context,
              title: 'Epikriz Raporu',
              subtitle: 'Hastane taburcu ve durum özetleri',
              icon: Icons.description,
              color: Colors.blue.shade600,
            ),
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

  Future<void> _pickPDF(BuildContext context, String reportType) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf'], // Sadece PDF formatına izin veriyoruz
        allowMultiple: false,
        withData: true,
      );

      if (context.mounted && result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        if (file.bytes != null) {
          Navigator.pop(context); // Seçim ekranını kapat
          Navigator.push(
            context,
            MaterialPageRoute(
              builder:
                  (context) => ResultScreen(
                    fileBytes:
                        file.bytes!, // ResultScreen artık fileBytes bekliyor
                    reportType: reportType,
                  ),
            ),
          );
        } else {
          _showError(context, 'PDF okunamadı (dosya boş olabilir).');
        }
      }
    } catch (e) {
      if (context.mounted) {
        _showError(context, 'PDF seçilirken hata oluştu: $e');
      }
    }
  }
}
