class Finding {
  final String severity, rule, target, path, message, domain, itemName;
  final int line;
  Finding({
    required this.severity, required this.rule, required this.target,
    required this.path, required this.line, required this.message,
    required this.domain, required this.itemName,
  });
  factory Finding.fromJson(Map<String, dynamic> j) {
    final c = (j['criteria'] ?? {}) as Map<String, dynamic>;
    return Finding(
      severity: j['severity'] ?? '', rule: j['rule'] ?? '',
      target: j['target'] ?? '', path: j['path'] ?? '',
      line: j['line'] ?? 0, message: j['message'] ?? '',
      domain: c['domain'] ?? '미분류', itemName: c['itemName'] ?? '',
    );
  }
}

class ScanResult {
  final List<Finding> findings;
  final Map<String, int> summary;
  final String reportPath;
  ScanResult({required this.findings, required this.summary, required this.reportPath});
  factory ScanResult.fromJson(Map<String, dynamic> j) => ScanResult(
        findings: ((j['findings'] ?? []) as List)
            .map((e) => Finding.fromJson(e as Map<String, dynamic>)).toList(),
        summary: Map<String, int>.from(
            (j['summary'] ?? {}).map((k, v) => MapEntry(k.toString(), v as int))),
        reportPath: j['reportPath'] ?? '',
      );
}
