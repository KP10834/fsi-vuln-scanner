import 'package:flutter_test/flutter_test.dart';
import 'package:fsi_scanner_app/services/engine_client.dart';

void main() {
  test('parseEngineOutput picks the result line', () {
    const out = '{"type":"warning","message":"skip"}\n'
        '{"type":"result","summary":{"CRITICAL":1},"reportPath":"r.html","findings":[]}\n';
    final result = EngineClient.parseEngineOutput(out);
    expect(result.summary['CRITICAL'], 1);
    expect(result.reportPath, 'r.html');
  });
}
