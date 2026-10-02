import 'dart:convert';
import 'dart:io';
import 'package:path/path.dart' as p;
import '../models/finding.dart';

class EngineClient {
  /// 번들된 엔진 실행파일 경로. 개발 중엔 python 모듈, 배포 시엔 engine.exe.
  static List<String> _command(List<String> args) {
    final exeDir = p.dirname(Platform.resolvedExecutable);
    final bundled = p.join(exeDir, 'engine', 'engine.exe');
    if (File(bundled).existsSync()) return [bundled, ...args];
    return ['python', '-m', 'engine.engine_cli', ...args]; // dev fallback
  }

  static Future<ScanResult> scan(List<String> targets, {String failOn = 'CRITICAL', required String outputDir}) async {
    final args = [
      '--targets', targets.join(','),
      '--fail-on', failOn,
      '--output-dir', outputDir,
      '--format', 'json',
    ];
    final cmd = _command(args);
    final proc = await Process.run(cmd.first, cmd.sublist(1), stdoutEncoding: utf8, stderrEncoding: utf8);
    if (proc.stdout.toString().trim().isEmpty) {
      throw Exception('엔진 실행 실패: ${proc.stderr}');
    }
    return parseEngineOutput(proc.stdout.toString());
  }

  static ScanResult parseEngineOutput(String stdout) {
    for (final line in const LineSplitter().convert(stdout).reversed) {
      if (line.trim().isEmpty) continue;
      final obj = jsonDecode(line) as Map<String, dynamic>;
      if (obj['type'] == 'result') return ScanResult.fromJson(obj);
    }
    throw Exception('엔진 결과(result) JSON을 찾을 수 없습니다.');
  }
}
