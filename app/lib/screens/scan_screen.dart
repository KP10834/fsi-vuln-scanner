import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_selector/file_selector.dart';
import 'package:desktop_drop/desktop_drop.dart';
import 'package:path/path.dart' as p;
import '../services/engine_client.dart';
import 'result_screen.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});
  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  final List<String> _targets = [];
  bool _running = false;
  bool _dragging = false;

  void _addTargets(Iterable<String> paths) {
    final added = paths
        .where((e) => Directory(e).existsSync() && !_targets.contains(e))
        .toList();
    if (added.isNotEmpty) setState(() => _targets.addAll(added));
  }

  Future<void> _addFolder() async {
    final dir = await getDirectoryPath();
    if (dir != null) _addTargets([dir]);
  }

  Future<void> _run() async {
    if (_targets.isEmpty) return;
    setState(() => _running = true);
    try {
      final outDir = p.join(Directory.systemTemp.path, 'fsi-scan-out');
      final result = await EngineClient.scan(_targets, outputDir: outDir);
      if (!mounted) return;
      Navigator.push(context, MaterialPageRoute(
        builder: (_) => ResultScreen(result: result)));
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('오류: $e')));
    } finally {
      if (mounted) setState(() => _running = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('FSI 취약점 분석')),
        body: DropTarget(
          onDragEntered: (_) => setState(() => _dragging = true),
          onDragExited: (_) => setState(() => _dragging = false),
          onDragDone: (d) {
            setState(() => _dragging = false);
            _addTargets(d.files.map((f) => f.path));
          },
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
              Row(children: [
                FilledButton.icon(onPressed: _addFolder,
                    icon: const Icon(Icons.add), label: const Text('대상 폴더 추가')),
                const SizedBox(width: 12),
                FilledButton.icon(
                    onPressed: _running || _targets.isEmpty ? null : _run,
                    icon: const Icon(Icons.play_arrow), label: const Text('스캔 실행')),
              ]),
              const SizedBox(height: 12),
              Expanded(child: _buildDropZone(context)),
              if (_running) const Padding(
                padding: EdgeInsets.only(top: 12),
                child: LinearProgressIndicator()),
            ]),
          ),
        ),
      );

  Widget _buildDropZone(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final border = _dragging ? scheme.primary : scheme.outlineVariant;
    final content = _targets.isEmpty
        ? Center(
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.folder_open,
                  size: 48, color: scheme.primary.withOpacity(0.7)),
              const SizedBox(height: 12),
              Text(_dragging ? '여기에 놓으세요' : '검사할 폴더를 여기로 드래그하거나',
                  style: Theme.of(context).textTheme.titleMedium),
              if (!_dragging) const Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text('위 [대상 폴더 추가] 버튼을 누르세요')),
            ]))
        : ListView(
            padding: const EdgeInsets.all(8),
            children: _targets.map((t) => ListTile(
              leading: const Icon(Icons.folder),
              title: Text(p.basename(t)), subtitle: Text(t),
              trailing: IconButton(icon: const Icon(Icons.close),
                  onPressed: () => setState(() => _targets.remove(t))),
            )).toList());
    return AnimatedContainer(
      duration: const Duration(milliseconds: 120),
      decoration: BoxDecoration(
        color: _dragging ? scheme.primary.withOpacity(0.06) : null,
        border: Border.all(color: border, width: _dragging ? 2 : 1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: content,
    );
  }
}
