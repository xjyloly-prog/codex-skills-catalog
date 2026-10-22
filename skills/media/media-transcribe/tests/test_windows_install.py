from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class WindowsInstallerContractTests(unittest.TestCase):
    def test_powershell_installer_has_component_parity_and_windows_venv(self):
        bash = (ROOT / "install.sh").read_text(encoding="utf-8")
        powershell = (ROOT / "install.ps1").read_text(encoding="utf-8")
        components = (
            "video", "douyin", "bilibili", "tiktok", "weibo", "zhihu", "youtube",
            "wechat-channels", "wechat-yuanbao", "podcast", "rss", "local-audio", "rss-download",
        )
        for component in components:
            with self.subTest(component=component):
                self.assertIn(component, bash)
                self.assertIn(f'"{component}"', powershell)
        self.assertIn('"Scripts\\python.exe"', powershell)
        self.assertIn('"curl.exe"', powershell)
        self.assertIn('"ffmpeg.exe"', powershell)
        self.assertIn('"ffprobe.exe"', powershell)
        self.assertIn("ExecutionPolicy", powershell)
        self.assertIn("$Component -join \",\"", powershell)
        self.assertIn("$Component[0] -split", powershell)
        self.assertIn("Executable = $candidate[0]", powershell)
        self.assertIn("$python.Executable", powershell)
        self.assertIn("Quote-PowerShellArgument", powershell)
        self.assertIn("$checkScript | & $VenvPython -", powershell)
        self.assertNotIn("& $VenvPython -c $checkScript", powershell)
        self.assertIn("sys.version_info >= (3, 9)", powershell)
        self.assertNotIn("repeatable", powershell)

    def test_windows_workflow_uses_windows_runner_and_scripts_python(self):
        workflow = (ROOT / ".github/workflows/windows.yml").read_text(encoding="utf-8")
        self.assertIn("runs-on: windows-latest", workflow)
        self.assertIn(r".\.venv\Scripts\python.exe", workflow)
        self.assertIn("shell: powershell", workflow)
        self.assertIn("-Component rss-download,local-audio", workflow)
        self.assertIn("install.ps1", workflow)
        self.assertIn("Start-Process powershell", workflow)
        self.assertIn("-RedirectStandardError $stderr", workflow)
        self.assertIn("$process.ExitCode", workflow)
        self.assertIn("unittest discover", workflow)
        self.assertIn("validate_evals.py", workflow)


if __name__ == "__main__":
    unittest.main()
