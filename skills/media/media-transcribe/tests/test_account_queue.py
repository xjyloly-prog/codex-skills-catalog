from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.account_queue import AccountQueue, AccountVideo, QueueLockedError


class AccountQueueTests(unittest.TestCase):
    def test_dedupes_orders_and_completes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            with AccountQueue(path) as queue:
                queue.upsert_account("sec", "https://www.douyin.com/user/sec", "oldest")
                videos = [
                    AccountVideo("new", "https://www.douyin.com/video/new", "New", 20),
                    AccountVideo("old", "https://www.douyin.com/video/old", "Old", 10),
                ]
                queue.add_videos("sec", videos)
                queue.add_videos("sec", videos)
                queue.reorder("sec", "oldest")
                self.assertEqual([row["video_id"] for row in queue.all_videos("sec")], ["old", "new"])
                first = queue.next_video("sec")
                self.assertEqual(first["video_id"], "old")
                queue.mark_completed("old", Path("old.md"))
                self.assertEqual(queue.counts("sec")["completed"], 1)

    def test_recovers_interrupted_and_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            with AccountQueue(path) as queue:
                queue.upsert_account("sec", "url", "oldest")
                queue.add_videos("sec", [AccountVideo("1", "url/1", "One")])
                queue.mark_state("1", "transcribing")
            with AccountQueue(path) as queue:
                self.assertEqual(queue.next_video("sec")["status"], "pending")
                self.assertEqual(queue.record_failure("1", "network"), "retry_wait")
                queue.db.execute("UPDATE videos SET next_attempt_at=0 WHERE video_id='1'")
                queue.db.commit()
                self.assertIsNotNone(queue.next_video("sec"))
                self.assertEqual(queue.record_failure("1", "network", max_attempts=2), "failed")
                self.assertEqual(queue.retry_failed("sec"), 1)

    def test_removes_stale_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            lock = path.with_suffix(".sqlite3.lock")
            lock.write_text("99999999")
            with AccountQueue(path):
                self.assertTrue(lock.is_file())
            self.assertFalse(lock.exists())

    def test_rejects_second_process_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.sqlite3"
            with AccountQueue(path):
                with self.assertRaises(QueueLockedError):
                    with AccountQueue(path):
                        pass


if __name__ == "__main__":
    unittest.main()
