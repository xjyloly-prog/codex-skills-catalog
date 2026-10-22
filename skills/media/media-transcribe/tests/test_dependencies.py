from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.dependencies import (
    SENSEVOICE_MODULES,
    dependency_spec_for_rss,
    dependency_spec_for_source,
    ensure_dependencies,
    install_command,
)


class DependencySpecTests(unittest.TestCase):
    def test_video_platforms_share_video_dependencies(self):
        expected_modules = SENSEVOICE_MODULES + ("yt_dlp",)
        for platform in ("bilibili", "tiktok", "weibo", "zhihu", "youtube"):
            with self.subTest(platform=platform):
                spec = dependency_spec_for_source(platform, f"https://{platform}.example/video")
                self.assertEqual(spec.component, platform)
                self.assertEqual(spec.modules, expected_modules)
                self.assertEqual(spec.commands, ("ffmpeg", "ffprobe"))

    def test_douyin_does_not_require_yt_dlp(self):
        spec = dependency_spec_for_source("douyin", "https://v.douyin.com/example/")
        self.assertEqual(spec.component, "douyin")
        self.assertEqual(spec.modules, SENSEVOICE_MODULES)
        self.assertEqual(spec.commands, ("curl", "ffmpeg"))

    def test_wechat_channels_uses_scoped_download_dependencies(self):
        spec = dependency_spec_for_source("wechat-channels", "https://weixin.qq.com/sph/example")
        self.assertEqual(spec.component, "wechat-channels")
        self.assertEqual(spec.modules, SENSEVOICE_MODULES)
        self.assertEqual(spec.commands, ("ffmpeg", "ffprobe"))

    def test_local_audio_only_requires_whisper(self):
        with tempfile.NamedTemporaryFile(suffix=".m4a") as audio:
            spec = dependency_spec_for_source("podcast", audio.name)
        self.assertEqual(spec.component, "local-audio")
        self.assertEqual(spec.modules, ("faster_whisper",))
        self.assertEqual(spec.commands, ())

    def test_remote_podcast_requires_whisper_and_curl(self):
        spec = dependency_spec_for_source("podcast", "https://example.com/episode")
        self.assertEqual(spec.component, "podcast")
        self.assertEqual(spec.modules, ("faster_whisper",))
        self.assertEqual(spec.commands, ("curl",))

    def test_rss_modes_have_scoped_dependencies(self):
        normal = dependency_spec_for_rss(False, False)
        download = dependency_spec_for_rss(True, False)
        transcribe = dependency_spec_for_rss(False, True)
        self.assertEqual((normal.component, normal.modules, normal.commands),
                         ("rss", ("faster_whisper",), ("curl",)))
        self.assertEqual((download.component, download.modules, download.commands),
                         ("rss-download", (), ("curl",)))
        self.assertEqual((transcribe.component, transcribe.modules, transcribe.commands),
                         ("rss", ("faster_whisper",), ("curl",)))

    @patch("media_transcribe.dependencies.importlib.import_module", side_effect=ImportError)
    @patch("media_transcribe.dependencies.shutil.which", return_value=None)
    def test_missing_dependencies_include_one_absolute_install_command(self, _which, _import_module):
        spec = dependency_spec_for_source("youtube", "https://youtu.be/example")
        with self.assertRaises(RuntimeError) as caught:
            ensure_dependencies(spec)
        message = str(caught.exception)
        self.assertIn("Python modules: funasr, modelscope, torch, torchaudio, yt_dlp", message)
        self.assertIn("system commands: ffmpeg, ffprobe", message)
        expected = install_command("youtube")
        self.assertIn(expected, message)
        installer = "install.ps1" if sys.platform == "win32" else "install.sh"
        self.assertIn(str(ROOT / installer), message)
        component_flag = "-Component 'youtube'" if sys.platform == "win32" else "--component youtube"
        self.assertEqual(message.count(component_flag), 1)

    def test_install_command_shell_quotes_special_paths(self):
        with patch("media_transcribe.dependencies.Path.resolve", return_value=Path("/tmp/O'Brien/scripts/media_transcribe/dependencies.py")):
            command = install_command("youtube", platform="posix")
        self.assertIn("O'\"'\"'Brien", command)

    def test_windows_install_command_uses_powershell_and_windows_installer(self):
        with patch(
            "media_transcribe.dependencies.Path.resolve",
            return_value=Path("C:/Users/O'Brien/media-transcribe/scripts/media_transcribe/dependencies.py"),
        ):
            command = install_command("youtube", platform="nt")
        self.assertIn("powershell -NoProfile -ExecutionPolicy Bypass", command)
        self.assertIn("install.ps1", command)
        self.assertIn("O''Brien", command)
        self.assertIn("-Component 'youtube'", command)
        self.assertNotIn("bash", command)

    @patch("media_transcribe.dependencies.importlib.import_module", return_value=object())
    @patch("media_transcribe.dependencies.shutil.which", return_value="/usr/bin/tool")
    def test_installed_dependencies_pass(self, _which, _import_module):
        ensure_dependencies(dependency_spec_for_source("douyin", "https://v.douyin.com/example/"))


if __name__ == "__main__":
    unittest.main()
