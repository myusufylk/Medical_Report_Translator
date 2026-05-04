import 'package:flutter/material.dart';
import 'report_model.dart';
import 'services/api_service.dart';
import 'result_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  // Gelecekte gelecek veriyi burada tanımlıyoruz
  late Future<List<MedicalReport>> _historyFuture;

  @override
  void initState() {
    super.initState();
    // Sayfa ilk açıldığında verileri çek
    _loadHistory();
  }

  // Verileri yükleme ve yenileme fonksiyonu
  void _loadHistory() {
    setState(() {
      _historyFuture = ApiService().getHistory();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F7FF), // Açık medikal mavi
      appBar: AppBar(
        title: const Text(
          'Geçmiş Raporlarım',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.black87),
        ),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
      ),
      // Aşağı çekince yenileme özelliği eklendi
      body: RefreshIndicator(
        onRefresh: () async {
          _loadHistory();
          // Future tamamlanana kadar refresh simgesini ekranda tutar
          await _historyFuture;
        },
        child: FutureBuilder<List<MedicalReport>>(
          future: _historyFuture,
          builder: (context, snapshot) {
            // 1. DURUM: Veri yükleniyor
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            // 2. DURUM: Hata oluştu
            if (snapshot.hasError) {
              return _buildErrorView(snapshot.error.toString());
            }

            // 3. DURUM: Veri boş geldi
            if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return _buildEmptyView();
            }

            // 4. DURUM: Başarılı, Listeyi göster
            final reports = snapshot.data!;
            return ListView.separated(
              // RefreshIndicator'ın her zaman çalışması için bu fizik şart
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              itemCount: reports.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final report = reports[index];
                return _buildHistoryCard(context, report);
              },
            );
          },
        ),
      ),
    );
  }

  // Liste elemanı tasarımı
  Widget _buildHistoryCard(BuildContext context, MedicalReport report) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.blue.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.blue.shade50,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(Icons.description_outlined, color: Colors.blue),
        ),
        title: Text(
          report.reportType, // Örn: Kan Tahlili
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(report.date), // Örn: 04.05.2026
        trailing: const Icon(Icons.chevron_right, color: Colors.grey),
        onTap: () {
          // Tıklayınca detay sayfasına yönlendir
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ResultScreen(report: report),
            ),
          );
        },
      ),
    );
  }

  // Boş liste görünümü
  Widget _buildEmptyView() {
    return ListView(
      // RefreshIndicator çalışması için Scrollable olması lazım
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        SizedBox(height: MediaQuery.of(context).size.height * 0.3),
        const Center(
          child: Column(
            children: [
              Icon(Icons.history_toggle_off, size: 64, color: Colors.grey),
              SizedBox(height: 16),
              Text(
                "Henüz bir rapor analizi yapmadınız.",
                style: TextStyle(color: Colors.grey, fontSize: 16),
              ),
            ],
          ),
        ),
      ],
    );
  }

  // Hata görünümü
  Widget _buildErrorView(String error) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        SizedBox(height: MediaQuery.of(context).size.height * 0.3),
        Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              children: [
                const Icon(Icons.error_outline, color: Colors.red, size: 48),
                const SizedBox(height: 16),
                Text(
                  "Bir sorun oluştu:\n$error",
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.black54),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _loadHistory,
                  child: const Text("Tekrar Dene"),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
