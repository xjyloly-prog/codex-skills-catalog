from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .account_queue import AccountQueue
from .downloaders import acquire_douyin
from .engines import load_sensevoice_model, transcribe_sensevoice
from .render import render_markdown, sanitize_filename, write_markdown
from .status import StatusReporter


class AccountWorker:
    def __init__(
        self,
        queue: AccountQueue,
        sec_uid: str,
        account_dir: Path,
        reporter: StatusReporter,
        max_attempts: int = 3,
        request_delay: float = 8.0,
        sleep=time.sleep,
    ):
        self.queue = queue
        self.sec_uid = sec_uid
        self.account_dir = account_dir
        self.reporter = reporter
        self.max_attempts = max_attempts
        self.request_delay = request_delay
        self.sleep = sleep
        self.transcripts_dir = account_dir / "transcripts"
        self.failures_path = account_dir / "failed" / "failures.jsonl"
        self.model = None

    def run(self) -> list[Path]:
        outputs: list[Path] = []
        counts = self.queue.counts(self.sec_uid)
        self.reporter.set_total(max(counts.get("total", 0), 1))
        while True:
            row = self.queue.next_video(self.sec_uid)
            if row is None:
                retry_at = self.queue.next_retry_at(self.sec_uid)
                if retry_at is None:
                    break
                wait_seconds = max(
                    retry_at - int(datetime.now(timezone.utc).timestamp()),
                    0,
                )
                self.reporter.stage(
                    "Waiting to retry failed video",
                    detail=f"retrying in {wait_seconds}s",
                )
                self.sleep(wait_seconds)
                continue
            position = row["queue_position"]
            total = counts.get("total", 0)
            video_id = row["video_id"]
            label = f"Video {position}/{total} · {video_id}"
            self.reporter.stage(f"{label}: Processing", detail=f"attempt {row['attempts'] + 1}/{self.max_attempts}")
            try:
                output = self._process(row, label)
                outputs.append(output)
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired,
                    RuntimeError, ValueError) as exc:
                message = str(exc)
                if _is_unavailable(message):
                    self.queue.mark_unavailable(video_id, message)
                    status = "unavailable"
                else:
                    status = self.queue.record_failure(video_id, message, self.max_attempts)
                self._append_failure(row, status, message)
                self.reporter.warning(f"{label} {status}: {message}")
            if self.request_delay:
                self.sleep(self.request_delay)
        self.write_summary()
        return outputs

    def _process(self, row, label: str) -> Path:
        video_id = row["video_id"]
        temp_dir = Path(tempfile.mkdtemp(prefix=f"media-account-{video_id}-"))
        try:
            self.queue.mark_state(video_id, "downloading")
            media = acquire_douyin(row["source_url"], temp_dir, self.reporter)
            self.reporter.stage(f"{label}: Download complete; preparing transcription")
            if self.model is None:
                self.reporter.stage("Loading shared SenseVoice-Small model")
                self.model = load_sensevoice_model()
            self.queue.mark_state(video_id, "transcribing")
            self.reporter.stage(f"{label}: Transcribing")
            with self.reporter.heartbeat(f"{label}: Transcription in progress"):
                transcript = transcribe_sensevoice(
                    str(media.audio_path), "zh", model=self.model, reporter=self.reporter,
                )
            self.queue.mark_state(video_id, "writing")
            self.reporter.stage(f"{label}: Writing Markdown")
            filename = (
                f"{row['queue_position']:04d}-{video_id}-"
                f"{sanitize_filename(media.title or row['title'], limit=60)}.md"
            )
            output = self.transcripts_dir / filename
            account = self.queue.account(self.sec_uid)
            content = render_markdown(
                media.title or row["title"],
                "douyin",
                row["source_url"],
                transcript,
                metadata={
                    "account_sec_uid": self.sec_uid,
                    "account_name": account["nickname"] if account else "",
                    "video_id": video_id,
                    "published_at": _published_iso(row["published_at"]),
                    "queue_position": row["queue_position"],
                },
            )
            write_markdown(output, content, overwrite=True)
            if not output.is_file() or output.stat().st_size == 0:
                raise RuntimeError("Markdown output was not created")
            self.queue.mark_completed(video_id, output)
            return output
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def write_summary(self) -> Path:
        account = self.queue.account(self.sec_uid)
        counts = self.queue.counts(self.sec_uid)
        rows = self.queue.all_videos(self.sec_uid)
        lines = [
            f"# {account['nickname'] or self.sec_uid} 转录进度",
            "",
            f"- 账号：{account['account_url']}",
            f"- 视频总数：{counts.get('total', 0)}",
            f"- 已完成：{counts.get('completed', 0)}",
            f"- 失败：{counts.get('failed', 0)}",
            f"- 不可用：{counts.get('unavailable', 0)}",
            f"- 待处理：{counts.get('pending', 0) + counts.get('retry_wait', 0)}",
            "",
            "## 视频",
            "",
        ]
        for row in rows:
            target = row["markdown_path"] or ""
            lines.append(
                f"- [{row['status']}] {row['queue_position']:04d} · {row['video_id']} · "
                f"{row['title']}" + (f" · `{target}`" if target else "")
            )
        path = self.account_dir / "summary.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".md.tmp")
        temporary.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        temporary.replace(path)
        account_json = self.account_dir / "account.json"
        account_json.write_text(json.dumps(dict(account), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def _append_failure(self, row, status: str, error: str) -> None:
        self.failures_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "video_id": row["video_id"],
            "status": status,
            "error": error,
            "time": datetime.now(timezone.utc).isoformat(),
        }
        with self.failures_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _published_iso(timestamp: int) -> str:
    if not timestamp:
        return ""
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


def _is_unavailable(message: str) -> bool:
    lowered = message.lower()
    return any(marker in lowered for marker in ("404", "not available", "deleted", "不可用", "已删除"))
