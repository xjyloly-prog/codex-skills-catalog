from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe import cli
from media_transcribe.account_enumerator import EnumerationPage
from media_transcribe.account_queue import AccountQueue, AccountVideo


class AccountCliTests(unittest.TestCase):
    def test_sync_only_creates_queue_and_summary_without_stdout(self):
        with tempfile.TemporaryDirectory() as directory:
            stdout = io.StringIO()
            stderr = io.StringIO()
            video = AccountVideo("1", "https://www.douyin.com/video/1", "One", 10)

            def enumerate_account(
                _url, max_videos=None, reporter=None, on_page=None, start_cursor="0",
                known_video_ids=None,
            ):
                page = EnumerationPage([video], "10", False, "Creator")
                if on_page:
                    on_page(page)
                return "MS4wLjAB_test", [video], "Creator", "10", True

            with (
                patch("media_transcribe.cli.ensure_opencli") as ensure_opencli,
                patch("media_transcribe.cli.ensure_dependencies") as ensure_dependencies,
                patch("media_transcribe.cli.enumerate_douyin_account", side_effect=enumerate_account),
                patch("sys.stdout", stdout),
                patch("sys.stderr", stderr),
            ):
                result = cli.main([
                    "--account-url", "https://www.douyin.com/user/MS4wLjAB_test",
                    "--sync-only", "-o", directory,
                ])
            self.assertEqual(result, 0)
            self.assertEqual(stdout.getvalue(), "")
            ensure_opencli.assert_called_once()
            ensure_dependencies.assert_not_called()
            account_dir = Path(directory) / "accounts" / "MS4wLjAB_test"
            self.assertTrue((account_dir / "queue.sqlite3").is_file())
            self.assertTrue((account_dir / "account.json").is_file())
            self.assertTrue((account_dir / "summary.md").is_file())

    def test_resumes_saved_cursor_without_resetting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            account_url = "https://www.douyin.com/user/MS4wLjAB_test"
            account_dir = Path(directory) / "accounts" / "MS4wLjAB_test"
            with AccountQueue(account_dir / "queue.sqlite3") as queue:
                queue.upsert_account("MS4wLjAB_test", account_url, "oldest", cursor="37")
                queue.add_videos("MS4wLjAB_test", [
                    AccountVideo("known", "https://www.douyin.com/video/known", "Known", 1),
                ])

            captured = {}

            def enumerate_account(
                _url, max_videos=None, reporter=None, on_page=None, start_cursor="0",
                known_video_ids=None,
            ):
                captured["start_cursor"] = start_cursor
                captured["known_video_ids"] = known_video_ids
                return "MS4wLjAB_test", [], "Creator", "37", False

            with (
                patch("media_transcribe.cli.ensure_opencli"),
                patch("media_transcribe.cli.enumerate_douyin_account", side_effect=enumerate_account),
                patch("sys.stdout", io.StringIO()),
                patch("sys.stderr", io.StringIO()),
            ):
                result = cli.main(["--account-url", account_url, "--sync-only", "-o", directory])
            self.assertEqual(result, 0)
            self.assertEqual(captured["start_cursor"], "37")
            self.assertEqual(captured["known_video_ids"], {"known"})
            with AccountQueue(account_dir / "queue.sqlite3") as queue:
                self.assertEqual(queue.account("MS4wLjAB_test")["last_cursor"], "37")

    def test_account_only_options_require_account_url(self):
        for options in (["--order", "newest"], ["--request-delay", "1"]):
            with self.subTest(options=options), patch("sys.stderr", io.StringIO()), \
                    self.assertRaises(SystemExit):
                cli.main(["/tmp/audio.mp3", *options])

    def test_processing_mode_checks_douyin_dependencies(self):
        args = cli.build_parser().parse_args([
            "--account-url", "https://www.douyin.com/user/MS4wLjAB_test",
        ])
        with (
            patch("media_transcribe.cli.ensure_opencli"),
            patch("media_transcribe.cli.ensure_dependencies") as ensure_dependencies,
            patch("media_transcribe.cli.AccountQueue", side_effect=RuntimeError("stop after preflight")),
            self.assertRaisesRegex(RuntimeError, "stop after preflight"),
        ):
            cli.transcribe_account(args, cli.StatusReporter(stream=io.StringIO()))
        self.assertEqual(ensure_dependencies.call_args.args[0].component, "douyin")


if __name__ == "__main__":
    unittest.main()
