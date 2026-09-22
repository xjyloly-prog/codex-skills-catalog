from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.wechat_yuanbao import (
    YuanbaoFallbackError,
    _IsolatedChrome,
    _find_chrome,
    _local_json,
    _parse_with_yuanbao,
    _trusted_playable_url,
)


class YuanbaoFallbackTests(unittest.TestCase):
    def test_playable_url_requires_official_https_origin(self):
        accepted = "https://channels.weixin.qq.com/finder-preview/pages/feed?token=x"
        self.assertEqual(_trusted_playable_url(accepted), accepted)
        for value in (
            "http://channels.weixin.qq.com/finder-preview/pages/feed",
            "https://channels.weixin.qq.com.example/finder-preview/pages/feed",
            "https://user@channels.weixin.qq.com/finder-preview/pages/feed",
        ):
            with self.subTest(value=value):
                with self.assertRaises(YuanbaoFallbackError):
                    _trusted_playable_url(value)

    def test_loopback_json_rejects_remote_debugger(self):
        with self.assertRaisesRegex(YuanbaoFallbackError, "non-loopback"):
            _local_json("http://example.com/json/list")

    def test_same_origin_request_contains_only_authorized_share_url(self):
        client = Mock()
        client.evaluate.return_value = {"status": 200, "ok": True, "data": {"code": 0}}
        source = "https://weixin.qq.com/sph/example"
        result = _parse_with_yuanbao(client, source)
        self.assertEqual(result["status"], 200)
        expression = client.evaluate.call_args.args[0]
        self.assertIn("https://yuanbao.tencent.com/api/weixin/get_parse_result", expression)
        self.assertIn("location.origin", expression)
        self.assertIn("document.readyState", expression)
        self.assertIn(source, expression)
        self.assertIn("credentials: 'same-origin'", expression)
        self.assertNotIn("document.cookie", expression)
        self.assertNotIn("localStorage", expression)

    def test_page_network_error_is_returned_as_retryable_wait(self):
        client = Mock()
        client.evaluate.return_value = {
            "waiting": True,
            "networkError": "TypeError: Failed to fetch",
            "page": {"origin": "https://yuanbao.tencent.com", "readyState": "interactive"},
        }
        result = _parse_with_yuanbao(client, "https://weixin.qq.com/sph/example")
        self.assertTrue(result["waiting"])
        self.assertIn("Failed to fetch", result["networkError"])

    def test_chrome_override_must_point_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            executable = Path(tmp) / "chrome"
            executable.write_text("")
            with patch.dict("os.environ", {"MEDIA_TRANSCRIBE_CHROME": str(executable)}):
                self.assertEqual(_find_chrome(), str(executable))

    def test_failed_chrome_startup_terminates_child(self):
        process = Mock()
        process.poll.return_value = None
        chrome = _IsolatedChrome(Path("/tmp/profile"))
        with (
            patch("media_transcribe.wechat_yuanbao._find_chrome", return_value="/tmp/chrome"),
            patch("media_transcribe.wechat_yuanbao.subprocess.Popen", return_value=process),
            patch("media_transcribe.wechat_yuanbao.time.monotonic", side_effect=(0, 31)),
            patch.object(Path, "mkdir"),
            patch.object(Path, "chmod"),
        ):
            with self.assertRaisesRegex(YuanbaoFallbackError, "Timed out"):
                chrome.__enter__()
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=8)


if __name__ == "__main__":
    unittest.main()
