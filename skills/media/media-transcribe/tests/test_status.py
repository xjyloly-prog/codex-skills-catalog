from __future__ import annotations

import io
import time
import unittest

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from media_transcribe.status import StatusReporter


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


class StatusReporterTests(unittest.TestCase):
    def test_non_tty_uses_plain_lines(self):
        stream = io.StringIO()
        ticks = iter((0.0, 1.0, 65.0))
        with StatusReporter(stream=stream, clock=lambda: next(ticks)) as reporter:
            reporter.set_total(2)
            reporter.stage("Downloading")
            reporter.stage("Transcribing", detail="segment 1/2")
        output = stream.getvalue()
        self.assertIn("[1/2] | Downloading · 00:01\n", output)
        self.assertIn("[2/2] | Transcribing · segment 1/2 · 01:05\n", output)
        self.assertNotIn("\r", output)
        self.assertNotIn("\x1b", output)

    def test_tty_renders_and_clears_one_line(self):
        stream = FakeTTY()
        reporter = StatusReporter(stream=stream, clock=lambda: 0.0, interval=10)
        with reporter:
            reporter.set_total(1)
            reporter.stage("Working")
        output = stream.getvalue()
        self.assertIn("\r\x1b[2K[1/1]", output)
        self.assertTrue(output.endswith("\r\x1b[2K"))
        self.assertIsNone(reporter._thread)

    def test_warning_is_permanent_and_status_resumes(self):
        stream = FakeTTY()
        with StatusReporter(stream=stream, clock=lambda: 0.0, interval=10) as reporter:
            reporter.stage("Downloading")
            reporter.warning("episode skipped")
        self.assertIn("warning: episode skipped\n", stream.getvalue())

    def test_suspend_stops_render_until_exit(self):
        stream = FakeTTY()
        with StatusReporter(stream=stream, clock=lambda: 0.0, interval=10) as reporter:
            reporter.stage("Loading model")
            with reporter.suspend():
                before = stream.getvalue()
                reporter.detail("library output active")
                self.assertEqual(before, stream.getvalue())
            self.assertGreater(len(stream.getvalue()), len(before))

    def test_repeated_non_tty_detail_is_deduplicated(self):
        stream = io.StringIO()
        with StatusReporter(stream=stream, clock=lambda: 0.0) as reporter:
            reporter.stage("Transcribing")
            reporter.detail("segment 1/1")
            reporter.detail("segment 1/1")
        self.assertEqual(stream.getvalue().count("segment 1/1"), 1)

    def test_non_tty_download_progress_is_throttled_by_ten_percent(self):
        stream = io.StringIO()
        with StatusReporter(stream=stream, clock=lambda: 0.0) as reporter:
            reporter.stage("Downloading")
            reporter.progress("11.0% · 1.1/10.0 MiB", 11.0)
            reporter.progress("19.0% · 1.9/10.0 MiB", 19.0)
            reporter.progress("20.0% · 2.0/10.0 MiB", 20.0)
            reporter.progress("100.0% · 10.0/10.0 MiB", 100.0)
        output = stream.getvalue()
        self.assertIn("11.0%", output)
        self.assertNotIn("19.0%", output)
        self.assertIn("20.0%", output)
        self.assertIn("100.0%", output)

    def test_tty_download_progress_updates_live_detail(self):
        stream = FakeTTY()
        with StatusReporter(stream=stream, clock=lambda: 0.0, interval=10) as reporter:
            reporter.stage("Downloading")
            reporter.progress("43.2% · ETA 00:05", 43.2)
        self.assertIn("43.2% · ETA 00:05", stream.getvalue())

    def test_forward_strips_control_sequences(self):
        stream = io.StringIO()
        with StatusReporter(stream=stream, clock=lambda: 0.0) as reporter:
            reporter.forward("\r\x1b[31mDownloading 50%\x1b[0m\n")
        self.assertEqual(stream.getvalue(), "Downloading 50%\n")

    def test_non_tty_heartbeat_reports_long_running_activity(self):
        stream = io.StringIO()
        with StatusReporter(stream=stream) as reporter:
            reporter.stage("Transcribing audio")
            with reporter.heartbeat("Transcription in progress", interval=0.01):
                deadline = time.monotonic() + 0.2
                while stream.getvalue().count("still working") < 2 and time.monotonic() < deadline:
                    time.sleep(0.005)
        output = stream.getvalue()
        self.assertIn("Transcription in progress · still working · 00:00", output)
        self.assertGreaterEqual(output.count("still working"), 2)

    def test_tty_heartbeat_relies_on_existing_spinner(self):
        stream = FakeTTY()
        with StatusReporter(stream=stream, interval=10) as reporter:
            reporter.stage("Transcribing audio")
            with reporter.heartbeat("Transcription in progress", interval=0.01):
                time.sleep(0.025)
        self.assertNotIn("still working", stream.getvalue())

    def test_exception_closes_worker(self):
        reporter = StatusReporter(stream=FakeTTY(), interval=0.01)
        with self.assertRaisesRegex(RuntimeError, "boom"):
            with reporter:
                reporter.stage("Working")
                time.sleep(0.02)
                raise RuntimeError("boom")
        self.assertIsNone(reporter._thread)


if __name__ == "__main__":
    unittest.main()
