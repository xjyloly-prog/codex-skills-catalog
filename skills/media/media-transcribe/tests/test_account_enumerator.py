from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.account_enumerator import (
    BrowserUnavailableError,
    EnumerationPage,
    LoginRequiredError,
    RateLimitedError,
    VerificationRequiredError,
    _fetch_page,
    _run_opencli,
    enumerate_douyin_account,
    extract_sec_uid,
)
from media_transcribe.account_queue import AccountVideo


class AccountEnumeratorTests(unittest.TestCase):
    def test_extracts_sec_uid_and_rejects_other_platforms(self):
        self.assertEqual(extract_sec_uid("https://www.douyin.com/user/MS4wLjAB_test"), "MS4wLjAB_test")
        self.assertEqual(extract_sec_uid("MS4wLjAB_test"), "MS4wLjAB_test")
        with self.assertRaisesRegex(ValueError, "Only Douyin"):
            extract_sec_uid("https://www.bilibili.com/user/1")

    @patch("media_transcribe.account_enumerator._run_opencli")
    @patch("media_transcribe.account_enumerator._fetch_page")
    def test_paginates_and_dedupes(self, fetch, run):
        one = AccountVideo("1", "url/1", "One", 1)
        two = AccountVideo("2", "url/2", "Two", 2)
        fetch.side_effect = [
            EnumerationPage([one, two], "20", True, "Creator"),
            EnumerationPage([two], "40", False, "Creator"),
        ]
        sec_uid, videos, nickname, cursor, complete = enumerate_douyin_account(
            "https://www.douyin.com/user/MS4wLjAB_test"
        )
        self.assertEqual(sec_uid, "MS4wLjAB_test")
        self.assertEqual([video.video_id for video in videos], ["1", "2"])
        self.assertEqual(nickname, "Creator")
        self.assertEqual(cursor, "40")
        self.assertTrue(complete)
        self.assertEqual(fetch.call_count, 2)
        run.assert_called_once()

    @patch("media_transcribe.account_enumerator._run_opencli")
    @patch("media_transcribe.account_enumerator._fetch_page")
    def test_limit_keeps_current_page_as_resume_checkpoint(self, fetch, run):
        videos = [AccountVideo(str(i), f"url/{i}", str(i), i) for i in range(5)]
        fetch.return_value = EnumerationPage(videos, "20", True, "Creator")
        persisted = []
        result = enumerate_douyin_account(
            "https://www.douyin.com/user/MS4wLjAB_test",
            max_videos=2,
            on_page=persisted.append,
            start_cursor="10",
        )
        self.assertEqual([video.video_id for video in result[1]], ["0", "1"])
        self.assertEqual([video.video_id for video in persisted[0].videos], ["0", "1"])
        self.assertEqual(persisted[0].cursor, "10")
        self.assertTrue(persisted[0].has_more)
        self.assertEqual(result[3], "10")
        self.assertFalse(result[4])

    @patch("media_transcribe.account_enumerator._run_opencli")
    @patch("media_transcribe.account_enumerator._fetch_page")
    def test_limit_equal_to_complete_page_marks_enumeration_complete(self, fetch, run):
        videos = [AccountVideo(str(i), f"url/{i}", str(i), i) for i in range(2)]
        fetch.return_value = EnumerationPage(videos, "20", False, "Creator")
        persisted = []
        result = enumerate_douyin_account(
            "https://www.douyin.com/user/MS4wLjAB_test",
            max_videos=2,
            on_page=persisted.append,
            start_cursor="10",
        )
        self.assertFalse(persisted[0].has_more)
        self.assertEqual(result[3], "20")
        self.assertTrue(result[4])

    @patch("media_transcribe.account_enumerator._run_opencli")
    @patch("media_transcribe.account_enumerator._fetch_page")
    def test_resume_same_page_skips_known_videos(self, fetch, run):
        videos = [AccountVideo(str(i), f"url/{i}", str(i), i) for i in range(5)]
        fetch.return_value = EnumerationPage(videos, "20", False, "Creator")
        result = enumerate_douyin_account(
            "https://www.douyin.com/user/MS4wLjAB_test",
            known_video_ids={"0", "1"},
            start_cursor="10",
        )
        self.assertEqual([video.video_id for video in result[1]], ["2", "3", "4"])
        self.assertEqual(result[3], "20")
        self.assertTrue(result[4])

    @patch("media_transcribe.account_enumerator._run_opencli")
    def test_classifies_login_expiry(self, run):
        envelope = {"http_status": 403, "body": "{}"}
        run.return_value.stdout = json.dumps(envelope)
        with self.assertRaises(LoginRequiredError):
            _fetch_page("sec", "0")

    @patch("media_transcribe.account_enumerator._run_opencli")
    def test_classifies_rate_limit_and_verification(self, run):
        run.return_value.stdout = json.dumps({"http_status": 429, "body": "{}"})
        with self.assertRaises(RateLimitedError):
            _fetch_page("sec", "0")
        run.return_value.stdout = json.dumps({
            "http_status": 200,
            "body": json.dumps({"status_code": 1, "status_msg": "captcha verify required"}),
        })
        with self.assertRaises(VerificationRequiredError):
            _fetch_page("sec", "0")

    @patch("media_transcribe.account_enumerator.subprocess.run", side_effect=FileNotFoundError)
    def test_classifies_missing_opencli(self, _run):
        with self.assertRaises(BrowserUnavailableError):
            _run_opencli(["doctor"])


if __name__ == "__main__":
    unittest.main()
