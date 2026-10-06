import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  MediaKit.ensureInitialized();
  runApp(const MaterialApp(home: PlaybackExample()));
}

class PlaybackExample extends StatefulWidget {
  const PlaybackExample({super.key});
  @override
  State<PlaybackExample> createState() => _PlaybackExampleState();
}

class _PlaybackExampleState extends State<PlaybackExample> {
  final _player = Player();
  final _url = TextEditingController();
  late final _video = VideoController(_player);
  bool _opening = false;

  Future<void> _open() async {
    final url = _url.text.trim();
    if (url.isEmpty || _opening) return;
    setState(() => _opening = true);
    try {
      await _player.open(Media(url));
    } catch (error) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not open media: $error')),
        );
      }
    } finally {
      if (mounted) setState(() => _opening = false);
    }
  }

  @override
  void dispose() {
    _url.dispose();
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(title: const Text('Android native playback')),
        body: Column(children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(children: [
              Expanded(
                  child: TextField(
                controller: _url,
                decoration: const InputDecoration(labelText: 'Media URL'),
                keyboardType: TextInputType.url,
                onSubmitted: (_) => _open(),
              )),
              const SizedBox(width: 12),
              FilledButton(
                onPressed: _opening ? null : _open,
                child: Text(_opening ? 'Opening...' : 'Open'),
              ),
            ]),
          ),
          Expanded(child: Video(controller: _video)),
        ]),
      );
}
