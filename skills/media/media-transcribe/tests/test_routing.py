from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.routing import detect_platform


class RoutingTests(unittest.TestCase):
    def test_routes_supported_platforms(self):
        cases = {
            "https://v.douyin.com/abc/": "douyin",
            "BV1xx411c7mD": "bilibili",
            "https://www.bilibili.com/video/BV1xx411c7mD": "bilibili",
            "https://vm.tiktok.com/abc": "tiktok",
            "https://weibo.com/tv/show/abc": "weibo",
            "https://www.zhihu.com/zvideo/123": "zhihu",
            "https://youtu.be/abc": "youtube",
            "https://weixin.qq.com/sph/example": "wechat-channels",
            "<https://weixin.qq.com/sph/example>": "wechat-channels",
            "https://www.xiaoyuzhoufm.com/episode/abc": "podcast",
            "https://cdn.example.com/download?file=audio.mp3": "podcast",
        }
        for source, expected in cases.items():
            with self.subTest(source=source):
                self.assertEqual(detect_platform(source), expected)

    def test_local_file_routes_to_podcast(self):
        with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
            self.assertEqual(detect_platform(audio.name), "podcast")

    def test_local_non_audio_file_is_rejected(self):
        with tempfile.NamedTemporaryFile(suffix=".md") as document:
            with self.assertRaisesRegex(ValueError, "not a supported audio file"):
                detect_platform(document.name)

    def test_lookalike_domain_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Cannot identify platform"):
            detect_platform("https://notyoutube.com/video/1")

    def test_wechat_channels_requires_exact_share_path(self):
        for source in (
            "http://weixin.qq.com/sph/example",
            "https://weixin.qq.com/sph/",
            "https://weixin.qq.com/sph/example/extra",
            "https://weixin.qq.com.example/sph/example",
            "https://weixin.qq.com:443/sph/example",
            "https://user@weixin.qq.com/sph/example",
        ):
            with self.subTest(source=source):
                with self.assertRaisesRegex(ValueError, "Cannot identify platform"):
                    detect_platform(source)

    def test_unknown_url_requires_explicit_platform(self):
        with self.assertRaisesRegex(ValueError, "Cannot identify platform"):
            detect_platform("https://example.com/watch/1")
        self.assertEqual(detect_platform("https://example.com/watch/1", "podcast"), "podcast")


if __name__ == "__main__":
    unittest.main()
