from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


ACTIVE_STATES = ("downloading", "extracting", "transcribing", "writing")
RETRY_DELAYS = (30, 120)


@dataclass(frozen=True)
class AccountVideo:
    video_id: str
    source_url: str
    title: str
    published_at: int = 0
    duration_ms: int = 0
    queue_position: int = 0


class QueueLockedError(RuntimeError):
    pass


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87
        kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


class AccountQueue:
    def __init__(self, path: Path):
        self.path = path
        self.lock_path = path.with_suffix(path.suffix + ".lock")
        self.connection: sqlite3.Connection | None = None
        self._lock_fd: int | None = None

    def __enter__(self) -> AccountQueue:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            if self._clear_stale_lock():
                self._lock_fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            else:
                raise QueueLockedError(f"Account queue is already in use: {self.lock_path}") from exc
        os.write(self._lock_fd, str(os.getpid()).encode())
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self._create_schema()
        self.recover_interrupted()
        return self

    def __exit__(self, _type, _value, _traceback) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if self._lock_fd is not None:
            os.close(self._lock_fd)
            self._lock_fd = None
        self.lock_path.unlink(missing_ok=True)

    def _clear_stale_lock(self) -> bool:
        try:
            pid = int(self.lock_path.read_text().strip())
        except ValueError:
            pid = 0
        if _pid_is_running(pid):
            return False
        self.lock_path.unlink(missing_ok=True)
        return True

    @property
    def db(self) -> sqlite3.Connection:
        if self.connection is None:
            raise RuntimeError("AccountQueue must be used as a context manager")
        return self.connection

    def _create_schema(self) -> None:
        self.db.executescript(
            """
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS accounts (
                platform TEXT NOT NULL,
                sec_uid TEXT PRIMARY KEY,
                account_url TEXT NOT NULL,
                nickname TEXT NOT NULL DEFAULT '',
                last_cursor TEXT NOT NULL DEFAULT '0',
                enumeration_complete INTEGER NOT NULL DEFAULT 0,
                order_mode TEXT NOT NULL DEFAULT 'oldest',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS videos (
                platform TEXT NOT NULL,
                video_id TEXT NOT NULL,
                account_sec_uid TEXT NOT NULL,
                source_url TEXT NOT NULL,
                title TEXT NOT NULL,
                published_at INTEGER NOT NULL DEFAULT 0,
                duration_ms INTEGER NOT NULL DEFAULT 0,
                queue_position INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                attempts INTEGER NOT NULL DEFAULT 0,
                next_attempt_at INTEGER NOT NULL DEFAULT 0,
                markdown_path TEXT,
                last_error TEXT,
                discovered_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (platform, video_id)
            );
            CREATE INDEX IF NOT EXISTS videos_queue_idx
              ON videos(account_sec_uid, status, next_attempt_at, queue_position);
            """
        )
        self.db.commit()

    def upsert_account(
        self,
        sec_uid: str,
        account_url: str,
        order_mode: str,
        nickname: str = "",
        cursor: str = "0",
        complete: bool = False,
    ) -> None:
        now = _now()
        self.db.execute(
            """
            INSERT INTO accounts
              (platform, sec_uid, account_url, nickname, last_cursor, enumeration_complete,
               order_mode, created_at, updated_at)
            VALUES ('douyin', ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sec_uid) DO UPDATE SET
              account_url=excluded.account_url,
              nickname=CASE WHEN excluded.nickname != '' THEN excluded.nickname ELSE accounts.nickname END,
              last_cursor=excluded.last_cursor,
              enumeration_complete=excluded.enumeration_complete,
              order_mode=excluded.order_mode,
              updated_at=excluded.updated_at
            """,
            (sec_uid, account_url, nickname, cursor, int(complete), order_mode, now, now),
        )
        self.db.commit()

    def add_videos(self, sec_uid: str, videos: list[AccountVideo]) -> int:
        now = _now()
        before = self.db.total_changes
        for video in videos:
            self.db.execute(
                """
                INSERT INTO videos
                  (platform, video_id, account_sec_uid, source_url, title, published_at,
                   duration_ms, queue_position, discovered_at, updated_at)
                VALUES ('douyin', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform, video_id) DO UPDATE SET
                  source_url=excluded.source_url,
                  title=excluded.title,
                  published_at=excluded.published_at,
                  duration_ms=excluded.duration_ms,
                  updated_at=excluded.updated_at
                """,
                (video.video_id, sec_uid, video.source_url, video.title, video.published_at,
                 video.duration_ms, video.queue_position, now, now),
            )
        self.db.commit()
        return self.db.total_changes - before

    def reorder(self, sec_uid: str, order_mode: str) -> None:
        direction = "ASC" if order_mode == "oldest" else "DESC"
        rows = self.db.execute(
            f"SELECT video_id FROM videos WHERE account_sec_uid=? ORDER BY published_at {direction}, video_id {direction}",
            (sec_uid,),
        ).fetchall()
        for position, row in enumerate(rows, 1):
            self.db.execute(
                "UPDATE videos SET queue_position=?, updated_at=? WHERE platform='douyin' AND video_id=?",
                (position, _now(), row["video_id"]),
            )
        self.db.execute("UPDATE accounts SET order_mode=?, updated_at=? WHERE sec_uid=?",
                        (order_mode, _now(), sec_uid))
        self.db.commit()

    def recover_interrupted(self) -> None:
        placeholders = ",".join("?" for _ in ACTIVE_STATES)
        self.db.execute(
            f"UPDATE videos SET status='pending', last_error='interrupted; retrying', updated_at=? "
            f"WHERE status IN ({placeholders})",
            (_now(), *ACTIVE_STATES),
        )
        self.db.commit()

    def retry_failed(self, sec_uid: str) -> int:
        cursor = self.db.execute(
            "UPDATE videos SET status='pending', attempts=0, next_attempt_at=0, last_error=NULL, updated_at=? "
            "WHERE account_sec_uid=? AND status='failed'",
            (_now(), sec_uid),
        )
        self.db.commit()
        return cursor.rowcount

    def next_video(self, sec_uid: str) -> sqlite3.Row | None:
        return self.db.execute(
            """
            SELECT * FROM videos
            WHERE account_sec_uid=? AND (
              status='pending' OR (status='retry_wait' AND next_attempt_at <= ?)
            )
            ORDER BY queue_position ASC
            LIMIT 1
            """,
            (sec_uid, int(datetime.now(timezone.utc).timestamp())),
        ).fetchone()

    def mark_state(self, video_id: str, status: str, error: str | None = None) -> None:
        self.db.execute(
            "UPDATE videos SET status=?, last_error=?, updated_at=? WHERE platform='douyin' AND video_id=?",
            (status, error, _now(), video_id),
        )
        self.db.commit()

    def mark_completed(self, video_id: str, markdown_path: Path) -> None:
        self.db.execute(
            "UPDATE videos SET status='completed', markdown_path=?, last_error=NULL, updated_at=? "
            "WHERE platform='douyin' AND video_id=?",
            (str(markdown_path), _now(), video_id),
        )
        self.db.commit()

    def mark_unavailable(self, video_id: str, error: str) -> None:
        self.mark_state(video_id, "unavailable", error)

    def record_failure(self, video_id: str, error: str, max_attempts: int = 3) -> str:
        row = self.db.execute(
            "SELECT attempts FROM videos WHERE platform='douyin' AND video_id=?", (video_id,)
        ).fetchone()
        attempts = (row["attempts"] if row else 0) + 1
        if attempts >= max_attempts:
            status, next_attempt = "failed", 0
        else:
            delay = RETRY_DELAYS[min(attempts - 1, len(RETRY_DELAYS) - 1)]
            status = "retry_wait"
            next_attempt = int(datetime.now(timezone.utc).timestamp()) + delay
        self.db.execute(
            "UPDATE videos SET status=?, attempts=?, next_attempt_at=?, last_error=?, updated_at=? "
            "WHERE platform='douyin' AND video_id=?",
            (status, attempts, next_attempt, error, _now(), video_id),
        )
        self.db.commit()
        return status

    def counts(self, sec_uid: str) -> dict[str, int]:
        rows = self.db.execute(
            "SELECT status, COUNT(*) AS count FROM videos WHERE account_sec_uid=? GROUP BY status",
            (sec_uid,),
        ).fetchall()
        result = {row["status"]: row["count"] for row in rows}
        result["total"] = sum(result.values())
        return result

    def next_retry_at(self, sec_uid: str) -> int | None:
        row = self.db.execute(
            "SELECT MIN(next_attempt_at) AS next_attempt_at FROM videos "
            "WHERE account_sec_uid=? AND status='retry_wait'",
            (sec_uid,),
        ).fetchone()
        return row["next_attempt_at"] if row and row["next_attempt_at"] is not None else None

    def video_ids(self, sec_uid: str) -> set[str]:
        rows = self.db.execute(
            "SELECT video_id FROM videos WHERE account_sec_uid=?", (sec_uid,)
        ).fetchall()
        return {row["video_id"] for row in rows}

    def account(self, sec_uid: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM accounts WHERE sec_uid=?", (sec_uid,)).fetchone()

    def all_videos(self, sec_uid: str) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT * FROM videos WHERE account_sec_uid=? ORDER BY queue_position", (sec_uid,)
        ).fetchall()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
