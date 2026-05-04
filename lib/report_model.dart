class MedicalReport {
  final String id;
  final String date;
  final String reportType;
  final String reportName; // Cemre'nin tablosunda bu da var
  final String aiResponse;
  final String status;

  MedicalReport({
    required this.id,
    required this.date,
    required this.reportType,
    required this.reportName,
    required this.aiResponse,
    required this.status,
  });

  factory MedicalReport.fromJson(Map<String, dynamic> json) {
    return MedicalReport(
      id: json['id']?.toString() ?? '',

      date: json['created_at'] ?? json['date'] ?? '',

      reportType: json['report_type'] ?? 'Genel Rapor',

      reportName: json['report_name'] ?? 'İsimsiz Rapor',

      aiResponse:
          json['summary_text'] ??
          json['ai_response'] ??
          'Analiz henüz hazır değil.',

      status: json['status'] ?? 'Analiz Edildi',
    );
  }
}
