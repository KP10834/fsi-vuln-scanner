import 'package:flutter/material.dart';
import 'screens/scan_screen.dart';

void main() => runApp(const FsiApp());

class FsiApp extends StatelessWidget {
  const FsiApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'FSI 취약점 분석',
        theme: ThemeData(colorSchemeSeed: const Color(0xFF4F6BFF), useMaterial3: true),
        home: const ScanScreen(),
      );
}
