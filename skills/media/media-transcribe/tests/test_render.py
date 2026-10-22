from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.models import Transcript
from media_transcribe.render import (
    normalize_transcript_text,
    output_path,
    render_markdown,
    sanitize_filename,
    write_markdown,
)


class RenderTests(unittest.TestCase):
    def test_yaml_quotes_titles_and_sources(self):
        transcript = Transcript("正文", "zh", "sensevoice-small", 1.2)
        result = render_markdown('标题: "测试"', "zhihu", "https://x.test/a?x=1#y", transcript)
        self.assertIn('title: "标题: \\"测试\\""', result)
        self.assertIn('source: "https://x.test/a?x=1#y"', result)
        self.assertIn("translated: false", result)
        self.assertIn("## Transcript\n\n正文", result)

    def test_filename_removes_windows_reserved_characters(self):
        self.assertEqual(sanitize_filename('项目<>:"/\\|?* 名称. '), "项目-名称")

    def test_bilingual_output_and_podcast_timestamps(self):
        bilingual = Transcript("English", "en", "sensevoice-small", 2.0, translated_text="中文")
        result = render_markdown("Title", "youtube", "https://youtu.be/x", bilingual)
        self.assertIn("translated: true", result)
        self.assertIn("## 中文翻译", result)
        self.assertIn("## English Original", result)

        podcast = Transcript("[   0.0s ->    1.0s] 内容", "zh", "faster-whisper-small", 3.0)
        result = render_markdown("播客", "podcast", "/tmp/a.mp3", podcast)
        self.assertIn("[   0.0s ->    1.0s] 内容", result)

    def test_wechat_channels_tag_and_source(self):
        transcript = Transcript("正文", "zh", "sensevoice-small", 1.0)
        result = render_markdown(
            "视频标题", "wechat-channels", "https://weixin.qq.com/sph/example", transcript,
        )
        self.assertIn('tags: ["视频号"]', result)
        self.assertIn('platform: "wechat-channels"', result)

    def test_video_renderer_rejects_unprocessed_timestamps(self):
        raw = "[   0.0s ->    1.0s] 第一句\n[   1.0s ->    2.0s] 第二句"
        with self.assertRaisesRegex(RuntimeError, "still contains timestamps"):
            normalize_transcript_text("wechat-channels", raw)
        transcript = Transcript(raw, "zh", "faster-whisper-small", 2.0)
        with self.assertRaisesRegex(RuntimeError, "still contains timestamps"):
            render_markdown(
                "视频标题", "wechat-channels", "https://weixin.qq.com/sph/example", transcript,
            )

    def test_podcast_keeps_timestamps_unchanged(self):
        raw = "[   0.0s ->    1.0s] 播客内容"
        self.assertEqual(normalize_transcript_text("podcast", raw), raw)

    def test_filename_and_atomic_overwrite_policy(self):
        self.assertEqual(sanitize_filename(' 标题: A/B? '), "标题-AB")
        with tempfile.TemporaryDirectory() as directory:
            path = output_path(Path(directory), "同名", "weibo")
            write_markdown(path, "one")
            with self.assertRaises(FileExistsError):
                write_markdown(path, "two")
            write_markdown(path, "two", overwrite=True)
            self.assertEqual(path.read_text(), "two")


if __name__ == "__main__":
    unittest.main()
