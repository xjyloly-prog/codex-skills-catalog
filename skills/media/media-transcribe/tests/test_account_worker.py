from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.account_queue import AccountQueue, AccountVideo
from media_transcribe.account_worker import AccountWorker
from media_transcribe.models import MediaSource, Transcript
from media_transcribe.status import StatusReporter


class AccountWorkerTests(unittest.TestCase):
    def test_continues_after_failure_and_reuses_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with AccountQueue(root / "queue.sqlite3") as queue:
                queue.upsert_account("sec", "https://www.douyin.com/user/sec", "oldest", "Creator")
                queue.add_videos("sec", [
                    AccountVideo("1", "https://www.douyin.com/video/1", "One", 1),
                    AccountVideo("2", "https://www.douyin.com/video/2", "Two", 2),
                ])
                queue.reorder("sec", "oldest")
                reporter = StatusReporter(stream=io.StringIO())
                with reporter, \
                    patch("media_transcribe.account_worker.acquire_douyin") as acquire, \
                    patch("media_transcribe.account_worker.load_sensevoice_model", return_value=object()) as load, \
                    patch("media_transcribe.account_worker.transcribe_sensevoice") as transcribe:
                    audio = root / "audio.mp3"
                    audio.write_bytes(b"audio")
                    acquire.side_effect = [OSError("disk unavailable"), MediaSource("douyin", "url", audio, "Two")]
                    transcribe.return_value = Transcript("正文", "zh", "sensevoice-small", 1.0)
                    worker = AccountWorker(queue, "sec", root, reporter, max_attempts=1, request_delay=0)
                    outputs = worker.run()
                self.assertEqual(len(outputs), 1)
                self.assertEqual(queue.counts("sec")["failed"], 1)
                self.assertEqual(queue.counts("sec")["completed"], 1)
                load.assert_called_once()
                self.assertTrue((root / "summary.md").is_file())
    def test_retries_waiting_item_in_same_run(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with AccountQueue(root / "queue.sqlite3") as queue:
                queue.upsert_account("sec", "https://www.douyin.com/user/sec", "oldest", "Creator")
                queue.add_videos("sec", [
                    AccountVideo("1", "https://www.douyin.com/video/1", "One", 1),
                ])
                queue.reorder("sec", "oldest")
                reporter = StatusReporter(stream=io.StringIO())
                sleeps = []

                def immediate_retry(seconds):
                    sleeps.append(seconds)
                    queue.db.execute("UPDATE videos SET next_attempt_at=0 WHERE video_id='1'")
                    queue.db.commit()

                with reporter, \
                    patch("media_transcribe.account_worker.acquire_douyin") as acquire, \
                    patch("media_transcribe.account_worker.load_sensevoice_model", return_value=object()), \
                    patch("media_transcribe.account_worker.transcribe_sensevoice") as transcribe:
                    audio = root / "audio.mp3"
                    audio.write_bytes(b"audio")
                    acquire.side_effect = [RuntimeError("temporary"), MediaSource("douyin", "url", audio, "One")]
                    transcribe.return_value = Transcript("正文", "zh", "sensevoice-small", 1.0)
                    worker = AccountWorker(
                        queue, "sec", root, reporter, max_attempts=2,
                        request_delay=0, sleep=immediate_retry,
                    )
                    outputs = worker.run()
                self.assertEqual(len(outputs), 1)
                self.assertEqual(queue.counts("sec")["completed"], 1)
                self.assertTrue(sleeps)


if __name__ == "__main__":
    unittest.main()
