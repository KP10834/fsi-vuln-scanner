import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/finding.dart';
import '../services/engine_client.dart';

class ResultScreen extends StatelessWidget {
  final ScanResult result;
  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('점검 결과'), actions: [
          TextButton.icon(
            onPressed: () => launchUrl(Uri.file(result.reportPath)),
            icon: const Icon(Icons.open_in_new),
            label: const Text('HTML 리포트 열기'),
          ),
        ]),
        body: Column(children: [
          Padding(
            padding: const EdgeInsets.all(12),
            child: Wrap(spacing: 8, children: result.summary.entries
                .map((e) => Chip(label: Text('${e.key}: ${e.value}'))).toList()),
          ),
          Expanded(child: ListView.builder(
            itemCount: result.findings.length,
            itemBuilder: (_, i) {
              final f = result.findings[i];
              return ListTile(
                dense: true,
                leading: _sevBadge(f.severity),
                title: Text('${f.message}  (${f.rule})'),
                subtitle: Text('[${f.target}] ${f.path}:${f.line}  · ${f.domain}'),
              );
            },
          )),
        ]),
      );

  Widget _sevBadge(String s) {
    final color = {
      'CRITICAL': Colors.red, 'HIGH': Colors.deepOrange,
      'MEDIUM': Colors.amber[800], 'LOW': Colors.blue,
    }[s] ?? Colors.grey;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(8)),
      child: Text(s, style: const TextStyle(color: Colors.white, fontSize: 11)),
    );
  }
}
