from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe import cli
from media_transcribe.models import MediaSource, Transcript
from media_transcribe.podcast import Episode


class CliStatusTests(unittest.TestCase):
    def test_single_item_keeps_stdout_path_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            audio = Path(tmp) / "audio.mp3"
            audio.write_bytes(b"audio")
            argv = ["https://youtu.be/example", "-o", str(output), "--no-translate"]
            stdout = io.StringIO()
            stderr = io.StringIO()
            media = MediaSource("youtube", argv[0], audio, "Example")
            transcript = Transcript("hello", "en", "sensevoice-small", 1.0)
            with (
                patch("media_transcribe.cli.ensure_dependencies"),
                patch("media_transcribe.cli.acquire_with_yt_dlp", return_value=media),
                patch("media_transcribe.cli.load_sensevoice_model", return_value=object()),
                patch("media_transcribe.cli.transcribe_sensevoice", return_value=transcript),
                patch("sys.stdout", stdout),
                patch("sys.stderr", stderr),
            ):
                self.assertEqual(cli.main(argv), 0)
            lines = stdout.getvalue().splitlines()
            self.assertEqual(len(lines), 1)
            self.assertTrue(lines[0].endswith("-youtube.md"))
            self.assertIn("Download complete; preparing transcription", stderr.getvalue())
            self.assertIn("Transcribing audio", stderr.getvalue())
            self.assertNotIn("\r", stderr.getvalue())

    def test_wechat_channels_uses_temp_media_and_keeps_markdown_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            source = "https://weixin.qq.com/sph/example"
            stdout = io.StringIO()
            stderr = io.StringIO()
            transcript = Transcript("正文", "zh", "sensevoice-small", 1.0)
            acquired_dirs = []

            def acquire(_source, temp_dir, reporter, *, consent, yuanbao_fallback):
                self.assertTrue(consent)
                self.assertFalse(yuanbao_fallback)
                acquired_dirs.append(temp_dir)
                video = temp_dir / "source.mp4"
                audio = temp_dir / "audio.mp3"
                video.write_bytes(b"video" * 3_000)
                audio.write_bytes(b"audio" * 3_000)
                return MediaSource("wechat-channels", source, audio, "视频标题")

            with (
                patch("media_transcribe.cli.ensure_dependencies"),
                patch("media_transcribe.cli.acquire_wechat_channels", side_effect=acquire),
                patch("media_transcribe.cli.load_sensevoice_model", return_value=object()),
                patch("media_transcribe.cli.transcribe_sensevoice", return_value=transcript),
                patch("sys.stdout", stdout),
                patch("sys.stderr", stderr),
            ):
                self.assertEqual(cli.main([source, "-o", str(output), "--allow-third-party-resolver"]), 0)

            lines = stdout.getvalue().splitlines()
            self.assertEqual(len(lines), 1)
            markdown = Path(lines[0])
            self.assertTrue(markdown.is_file())
            self.assertTrue(markdown.name.endswith("-wechat-channels.md"))
            self.assertFalse(acquired_dirs[0].exists())
            self.assertEqual(list(output.glob("*.mp4")), [])
            self.assertEqual(list(output.glob("*.mp3")), [])

    def test_wechat_channels_requires_explicit_resolver_consent(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch("sys.stdout", stdout), patch("sys.stderr", stderr):
            self.assertEqual(cli.main(["https://weixin.qq.com/sph/example"]), 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("--allow-third-party-resolver", stderr.getvalue())

    def test_yuanbao_fallback_requires_both_consents(self):
        with self.assertRaises(SystemExit):
            cli.main([
                "https://weixin.qq.com/sph/example",
                "--allow-yuanbao-fallback",
            ])

    def test_yuanbao_fallback_is_rejected_for_other_platforms(self):
        with self.assertRaises(SystemExit):
            cli.main([
                "https://youtu.be/example",
                "--allow-third-party-resolver",
                "--allow-yuanbao-fallback",
            ])

    def test_rss_download_only_has_empty_stdout_and_audio_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output"
            stdout = io.StringIO()
            stderr = io.StringIO()
            episode = Episode(1, "Example", "2026-01-01", "01:00", 60, "https://example.com/1.mp3")

            def download(_url, destination):
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(b"audio" * 3_000)
                return destination

            with (
                patch("media_transcribe.cli.ensure_dependencies"),
                patch("media_transcribe.cli.parse_rss", return_value=[episode]),
                patch("media_transcribe.cli.download_url", side_effect=download),
                patch("media_transcribe.cli.load_whisper_model") as load_model,
                patch("media_transcribe.cli.transcribe_whisper") as transcribe,
                patch("sys.stdout", stdout),
                patch("sys.stderr", stderr),
            ):
                result = cli.main([
                    "--rss-url", "https://example.com/feed.xml", "--download-only",
                    "--count", "1", "-o", str(output),
                ])

            self.assertEqual(result, 0)
            self.assertEqual(stdout.getvalue(), "")
            self.assertTrue((output / "audio" / "EP001-Example.mp3").is_file())
            self.assertEqual(list(output.glob("*.md")), [])
            load_model.assert_not_called()
            transcribe.assert_not_called()

    def test_error_closes_status_before_diagnostic(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch("media_transcribe.cli.ensure_dependencies"),
            patch("media_transcribe.cli.acquire_douyin", side_effect=RuntimeError("download failed")),
            patch("sys.stdout", stdout),
            patch("sys.stderr", stderr),
        ):
            self.assertEqual(cli.main(["https://v.douyin.com/example/"]), 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertTrue(stderr.getvalue().rstrip().endswith("error: download failed"))


if __name__ == "__main__":
    unittest.main()
