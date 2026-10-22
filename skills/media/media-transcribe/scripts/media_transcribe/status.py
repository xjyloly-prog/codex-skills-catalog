from __future__ import annotations

import contextlib
import re
import sys
import threading
import time
from collections.abc import Iterator
from typing import TextIO


class StatusReporter:
    FRAMES = ("|", "/", "-", "\\")

    def __init__(
        self,
        stream: TextIO | None = None,
        clock=time.monotonic,
        interval: float = 0.2,
    ) -> None:
        self.stream = stream or sys.stderr
        self.clock = clock
        self.interval = interval
        try:
            self.tty = bool(self.stream.isatty())
        except (AttributeError, OSError):
            self.tty = False
        self.current = 0
        self.total: int | None = None
        self.label = ""
        self.detail_text = ""
        self.started = 0.0
        self.suspended = False
        self._last_plain_detail = ""
        self._last_progress_bucket = -1
        self._frame = 0
        self._line_visible = False
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def __enter__(self) -> StatusReporter:
        self.started = self.clock()
        if self.tty:
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, _type, _value, _traceback) -> None:
        self.close()

    def set_total(self, total: int) -> None:
        with self._lock:
            self.total = total
            self._render_locked()

    def extend_total(self, count: int) -> None:
        if count < 1:
            return
        with self._lock:
            self.total = (self.total or self.current) + count
            self._render_locked()

    def stage(self, label: str, *, detail: str = "") -> None:
        with self._lock:
            self.current += 1
            self.label = label
            self.detail_text = detail
            self._last_plain_detail = detail
            self._last_progress_bucket = -1
            if self.tty:
                self._render_locked()
            else:
                self._write_line_locked(self._status_text())

    def detail(self, message: str) -> None:
        with self._lock:
            self.detail_text = message
            if self.tty:
                self._render_locked()
            elif message != self._last_plain_detail:
                self._write_line_locked(f"  {message}")
                self._last_plain_detail = message

    def progress(self, message: str, percent: float | None = None) -> None:
        with self._lock:
            self.detail_text = message
            if self.tty:
                self._render_locked()
                return
            if percent is None:
                if message != self._last_plain_detail:
                    self._write_line_locked(f"  {message}")
                    self._last_plain_detail = message
                return
            bucket = min(int(percent) // 10, 10)
            if bucket > self._last_progress_bucket:
                self._write_line_locked(f"  {message}")
                self._last_plain_detail = message
                self._last_progress_bucket = bucket

    def warning(self, message: str) -> None:
        with self._lock:
            self._clear_locked()
            self._write_line_locked(f"warning: {message}")
            self._render_locked()

    def forward(self, text: str) -> None:
        for line in text.splitlines():
            clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", line).replace("\r", "").strip()
            if clean:
                with self._lock:
                    self._clear_locked()
                    self._write_line_locked(clean)
                    self._render_locked()

    @contextlib.contextmanager
    def heartbeat(self, message: str, interval: float = 15.0) -> Iterator[None]:
        if self.tty:
            yield
            return
        stop = threading.Event()
        started = self.clock()

        def emit() -> None:
            while not stop.wait(interval):
                elapsed = max(0, int(self.clock() - started))
                minutes, seconds = divmod(elapsed, 60)
                hours, minutes = divmod(minutes, 60)
                duration = (
                    f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    if hours else f"{minutes:02d}:{seconds:02d}"
                )
                with self._lock:
                    self._write_line_locked(f"  {message} · still working · {duration}")

        worker = threading.Thread(target=emit, daemon=True)
        worker.start()
        try:
            yield
        finally:
            stop.set()
            worker.join(timeout=max(interval * 2, 0.2))

    @contextlib.contextmanager
    def suspend(self) -> Iterator[None]:
        with self._lock:
            if self.tty and self.label:
                self._clear_locked()
                self._write_line_locked(self._status_text())
            self.suspended = True
        try:
            yield
        finally:
            with self._lock:
                self.suspended = False
                self._render_locked()

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(self.interval * 2, 0.2))
            self._thread = None
        with self._lock:
            if self.tty and self._line_visible:
                self.stream.write("\r\x1b[2K")
                self.stream.flush()
                self._line_visible = False

    def _spin(self) -> None:
        while not self._stop.wait(self.interval):
            with self._lock:
                if self.label and not self.suspended:
                    self._frame = (self._frame + 1) % len(self.FRAMES)
                    self._render_locked()

    def _status_text(self) -> str:
        total = str(self.total) if self.total is not None else "?"
        elapsed = max(0, int(self.clock() - self.started))
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
        detail = f" · {self.detail_text}" if self.detail_text else ""
        return f"[{self.current}/{total}] {self.FRAMES[self._frame]} {self.label}{detail} · {duration}"

    def _render_locked(self) -> None:
        if not self.tty or not self.label or self.suspended:
            return
        self.stream.write(f"\r\x1b[2K{self._status_text()}")
        self.stream.flush()
        self._line_visible = True

    def _clear_locked(self) -> None:
        if self.tty and self._line_visible:
            self.stream.write("\r\x1b[2K")
            self.stream.flush()
            self._line_visible = False

    def _write_line_locked(self, message: str) -> None:
        self.stream.write(f"{message}\n")
        self.stream.flush()
