from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractTests(unittest.TestCase):
    def test_readme_distinguishes_agent_and_direct_cli_behavior(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Agent 入口与直接 CLI 的区别", readme)
        self.assertIn("CLI 不会弹出选择题", readme)
        self.assertIn("不会自动安装或重试", readme)
        self.assertIn("退出码 `2`", readme)
        self.assertNotIn("CLI 会停止并提示是否", readme)

    def test_wechat_method_attribution_is_in_readme_license_section(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        source = "https://github.com/joeseesun/qiaomu-wx-video"
        license_section = readme.split("## License", 1)[1]
        self.assertIn(source, license_section)
        self.assertIn("视频号下载方法总结与安全边界参考自", license_section)
        self.assertIn("本项目为独立实现", license_section)
        self.assertNotIn(source, license_text)

    def test_runtime_status_examples_match_current_stage_contract(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        status = readme.split("## 运行状态", 1)[1].split("## 输出", 1)[0]
        self.assertIn("普通 yt-dlp 视频当前为 8 个阶段", status)
        self.assertIn("视频号隔离元宝降级为 13 个", status)
        self.assertIn("[8/8] | Writing Markdown", status)
        self.assertIn("[13/13] | Writing Markdown", status)
        self.assertIn("100.0%", status)
        self.assertIn("视频号临时媒体下载当前只能可靠显示阶段", status)
        self.assertIn("心跳表示进程仍在运行，不是精确完成百分比", status)
        self.assertNotIn("[5/9]", status)
        self.assertNotIn("[2/9]", status)

    def test_cleanup_claims_are_scoped_as_best_effort(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("尽力清理", readme)
        self.assertIn("尽力清理", skill)
        self.assertNotIn("无论成功、失败或可捕获的键盘中断", readme)


if __name__ == "__main__":
    unittest.main()
