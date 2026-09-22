from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.downloaders import (
    PROFILES,
    WechatResolverUnavailableError,
    _parse_progress_line,
    _yt_dlp_command,
    normalize_bilibili_source,
    normalize_wechat_channels_url,
    resolver_error_message,
    parse_douyin_router_data,
    parse_wechat_channels_profile,
    request_json,
    acquire_wechat_channels,
    run_yt_dlp,
)


class DownloaderTests(unittest.TestCase):
    def test_profiles_preserve_platform_settings(self):
        self.assertEqual(PROFILES["tiktok"].extra_args, ("--geo-bypass",))
        self.assertEqual(PROFILES["tiktok"].language, "auto")
        self.assertEqual(PROFILES["weibo"].language, "zh")
        self.assertIn("weibo.com", PROFILES["weibo"].referer)
        self.assertIn("zhihu.com", PROFILES["zhihu"].referer)
        self.assertIn("youtube.com", PROFILES["youtube"].referer)

    def test_normalizes_bvid(self):
        self.assertEqual(
            normalize_bilibili_source("BV1xx411c7mD"),
            "https://www.bilibili.com/video/BV1xx411c7mD",
        )

    @patch("media_transcribe.downloaders.subprocess.run")
    def test_metadata_yt_dlp_is_quiet_and_captured(self, run):
        run_yt_dlp(PROFILES["youtube"], ["--get-title", "https://youtu.be/x"], 60)
        command = run.call_args.args[0]
        self.assertIn("--no-progress", command)
        self.assertTrue(run.call_args.kwargs["capture_output"])
        self.assertTrue(run.call_args.kwargs["text"])

    def test_download_command_uses_machine_readable_progress(self):
        command = _yt_dlp_command(
            PROFILES["bilibili"], ["--extract-audio", "https://example.test/video"],
            show_progress=True,
        )
        self.assertIn("--newline", command)
        self.assertIn("--progress", command)
        self.assertIn("--progress-template", command)
        self.assertNotIn("--no-progress", command)

    def test_progress_template_is_read_from_stdout(self):
        class FakeProcess:
            def __init__(self):
                self.stdout = io.StringIO(
                    "MT_PROGRESS|downloading|5242880|10485760|NA|1048576|5\n"
                )
                self.stderr = io.StringIO("")

            def wait(self, timeout=None):
                return 0

        reporter = Mock()
        with patch("media_transcribe.downloaders.subprocess.Popen", return_value=FakeProcess()):
            from media_transcribe.downloaders import run_yt_dlp_with_progress
            run_yt_dlp_with_progress(
                PROFILES["bilibili"], ["https://example.test/video"], 60, reporter,
            )
        reporter.progress.assert_called_once_with(
            "50.0% · 5.0/10.0 MiB · 1.0 MiB/s · ETA 00:05", 50.0,
        )

    def test_parses_machine_readable_progress(self):
        parsed = _parse_progress_line("MT_PROGRESS|downloading|12582912|30513562|NA|3984588|5")
        self.assertAlmostEqual(parsed.percent, 41.24, places=2)
        self.assertEqual(parsed.text, "41.2% · 12.0/29.1 MiB · 3.8 MiB/s · ETA 00:05")
        estimated = _parse_progress_line("MT_PROGRESS|downloading|5242880|NA|10485760|0|NA")
        self.assertEqual(estimated.percent, 50.0)
        self.assertIn("5.0/~10.0 MiB", estimated.text)
        self.assertIsNone(_parse_progress_line("[download] Destination: x"))

    def test_wechat_channels_url_normalization_is_strict(self):
        self.assertEqual(
            normalize_wechat_channels_url(" https://weixin.qq.com/sph/example?x=1#part "),
            "https://weixin.qq.com/sph/example?x=1",
        )
        for source in (
            "http://weixin.qq.com/sph/example",
            "https://weixin.qq.com/sph/",
            "https://weixin.qq.com/sph/example/extra",
            "https://weixin.qq.com.example/sph/example",
        ):
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    normalize_wechat_channels_url(source)

    def test_wechat_profile_selects_one_h264_url_and_metadata(self):
        profile = {
            "errCode": 0,
            "data": {
                "authorInfo": {"nickname": "作者"},
                "feedInfo": {
                    "description": "标题第一行\n#标签",
                    "h264VideoInfo": {"videoUrl": "https://finder.video.qq.com/video-h264"},
                    "h265VideoInfo": {"videoUrl": "https://finder.video.qq.com/video-h265"},
                    "videoUrl": "https://finder.video.qq.com/video-default",
                    "createtime": 123,
                },
            },
        }
        title, media_url, metadata = parse_wechat_channels_profile(profile)
        self.assertEqual(title, "标题第一行")
        self.assertEqual(media_url, "https://finder.video.qq.com/video-h264")
        self.assertEqual(metadata, {"author": "作者", "published_at": "123"})

    def test_wechat_resolver_unauthorized_error_is_actionable(self):
        message = resolver_error_message("parse share url: parseShareUrl: http 401", 500)
        self.assertIn("credentials are unavailable or expired", message)
        self.assertIn("try again later", message)
        self.assertNotIn("HTTP 500", message)

    @patch("media_transcribe.downloaders.urllib.request.urlopen", side_effect=TimeoutError)
    def test_wechat_resolver_timeout_is_fallback_eligible(self, _urlopen):
        with self.assertRaisesRegex(WechatResolverUnavailableError, "timed out"):
            request_json("https://resolver.example/api", {"url": "https://weixin.qq.com/sph/x"})

    def test_wechat_profile_rejects_malformed_feed(self):
        with self.assertRaisesRegex(RuntimeError, "missing feed information"):
            parse_wechat_channels_profile({"errCode": 0, "data": {"feedInfo": None}})

    def test_wechat_profile_strips_controls_from_errors(self):
        with self.assertRaises(RuntimeError) as caught:
            parse_wechat_channels_profile({"errCode": 1, "errMsg": "bad\x1b]8;;https://evil.test\x07link"})
        message = str(caught.exception)
        self.assertNotIn("\x1b", message)
        self.assertNotIn("\x07", message)

    def test_wechat_profile_rejects_untrusted_media_host(self):
        profile = {
            "errCode": 0,
            "data": {"feedInfo": {"h264VideoInfo": {"videoUrl": "https://example.com/video"}}},
        }
        with self.assertRaisesRegex(RuntimeError, "unexpected host"):
            parse_wechat_channels_profile(profile)

    @patch("media_transcribe.downloaders.subprocess.run")
    @patch("media_transcribe.downloaders.download_wechat_media")
    @patch("media_transcribe.downloaders.request_json")
    def test_wechat_acquisition_downloads_one_video_and_extracts_audio(
        self, request_json, download_media, run,
    ):
        request_json.return_value = {
            "errCode": 0,
            "data": {
                "authorInfo": {"nickname": "作者"},
                "feedInfo": {
                    "description": "标题",
                    "h264VideoInfo": {"videoUrl": "https://finder.video.qq.com/video-h264"},
                    "h265VideoInfo": {"videoUrl": "https://finder.video.qq.com/video-h265"},
                },
            },
        }

        def download_side_effect(url, destination, **_kwargs):
            self.assertEqual(url, "https://finder.video.qq.com/video-h264")
            destination.write_bytes(b"video" * 3_000)

        def command_side_effect(command, **_kwargs):
            if command[0] == "ffprobe":
                return Mock(stdout=json.dumps({
                    "format": {"duration": "12.5"},
                    "streams": [{"codec_type": "video"}, {"codec_type": "audio"}],
                }))
            elif command[0] == "ffmpeg":
                Path(command[-1]).write_bytes(b"audio" * 3_000)
            return Mock(stdout="")

        download_media.side_effect = download_side_effect
        run.side_effect = command_side_effect
        with tempfile.TemporaryDirectory() as tmp:
            media = acquire_wechat_channels(
                "https://weixin.qq.com/sph/example", Path(tmp), consent=True,
            )
            self.assertEqual(media.platform, "wechat-channels")
            self.assertTrue(media.audio_path.is_file())
            download_media.assert_called_once()

    @patch("media_transcribe.downloaders.prepare_wechat_media")
    @patch("media_transcribe.wechat_yuanbao.resolve_via_yuanbao")
    @patch("media_transcribe.downloaders.request_json")
    def test_wechat_uses_yuanbao_only_for_unavailable_public_resolver(
        self, request_json, resolve_yuanbao, prepare_media,
    ):
        from media_transcribe.wechat_yuanbao import YuanbaoResult

        request_json.side_effect = WechatResolverUnavailableError("public unavailable")
        resolve_yuanbao.return_value = YuanbaoResult(
            "标题", "https://finder.video.qq.com/video", {"acquisition": "yuanbao-same-origin"},
        )
        prepared = Mock()
        prepare_media.return_value = prepared
        with tempfile.TemporaryDirectory() as tmp:
            result = acquire_wechat_channels(
                "https://weixin.qq.com/sph/example",
                Path(tmp),
                consent=True,
                yuanbao_fallback=True,
            )
        self.assertIs(result, prepared)
        resolve_yuanbao.assert_called_once()

    @patch("media_transcribe.downloaders.request_json")
    def test_wechat_public_failure_prompts_for_yuanbao_without_running_it(self, request_json):
        request_json.side_effect = WechatResolverUnavailableError("public unavailable")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(WechatResolverUnavailableError, "--allow-yuanbao-fallback"):
                acquire_wechat_channels(
                    "https://weixin.qq.com/sph/example", Path(tmp), consent=True,
                )

    def test_parses_douyin_router_data_and_removes_watermark(self):
        payload = {
            "loaderData": {
                "video_(id)/page": {
                    "videoInfoRes": {
                        "item_list": [{
                            "desc": "标题",
                            "video": {"play_addr": {"url_list": ["https://x/playwm?id=1"]}},
                        }]
                    }
                }
            }
        }
        html = f"<script>window._ROUTER_DATA = {json.dumps(payload)};</script>"
        title, url = parse_douyin_router_data(html)
        self.assertEqual(title, "标题")
        self.assertEqual(url, "https://x/play?id=1")


if __name__ == "__main__":
    unittest.main()
