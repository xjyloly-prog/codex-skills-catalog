from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlparse

from .account_queue import AccountVideo
from .status import StatusReporter


class AccountEnumerationError(RuntimeError):
    pass


class BrowserUnavailableError(AccountEnumerationError):
    pass


class LoginRequiredError(AccountEnumerationError):
    pass


class RateLimitedError(AccountEnumerationError):
    pass


class VerificationRequiredError(AccountEnumerationError):
    pass


@dataclass(frozen=True)
class EnumerationPage:
    videos: list[AccountVideo]
    cursor: str
    has_more: bool
    nickname: str = ""


def extract_sec_uid(account_url: str) -> str:
    if not account_url.startswith(("http://", "https://")):
        if re.fullmatch(r"MS4wLjAB[A-Za-z0-9_-]+", account_url):
            return account_url
        raise ValueError("Provide a Douyin account URL or sec_uid")
    parsed = urlparse(account_url)
    host = parsed.netloc.lower().split(":", 1)[0]
    if host != "douyin.com" and not host.endswith(".douyin.com"):
        raise ValueError("Only Douyin account URLs are supported in account mode")
    match = re.search(r"/user/([^/?#]+)", parsed.path)
    if not match:
        raise ValueError("Cannot extract sec_uid from Douyin account URL")
    return match.group(1)


def _run_opencli(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["opencli", *args], capture_output=True, text=True, timeout=timeout, check=True,
        )
    except FileNotFoundError as exc:
        raise BrowserUnavailableError("OpenCLI is not installed or not on PATH") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        raise BrowserUnavailableError(f"OpenCLI browser command failed: {detail}") from exc


def _fetch_page(sec_uid: str, cursor: str, count: int = 20) -> EnumerationPage:
    endpoint = (
        "https://www.douyin.com/aweme/v1/web/aweme/post/"
        f"?sec_user_id={sec_uid}&max_cursor={cursor}&count={count}&aid=6383"
    )
    script = f"""
(async () => {{
  const response = await fetch({json.dumps(endpoint)}, {{credentials: 'include'}});
  const text = await response.text();
  return JSON.stringify({{http_status: response.status, body: text}});
}})()
""".strip()
    result = _run_opencli(["operate", "eval", script], timeout=90)
    try:
        envelope = json.loads(result.stdout)
        http_status = int(envelope["http_status"])
        body = json.loads(envelope["body"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise AccountEnumerationError("Douyin account response was not valid JSON") from exc

    if http_status == 429:
        raise RateLimitedError("Douyin rate limited account enumeration (HTTP 429)")
    if http_status in (401, 403):
        raise LoginRequiredError(f"Douyin login is required or expired (HTTP {http_status})")
    if http_status >= 400:
        raise AccountEnumerationError(f"Douyin account request failed (HTTP {http_status})")

    status_code = body.get("status_code", 0)
    status_message = str(body.get("status_msg", ""))
    lower_message = status_message.lower()
    if status_code:
        if "verify" in lower_message or "captcha" in lower_message or "验证码" in status_message:
            raise VerificationRequiredError(f"Douyin verification is required: {status_message}")
        if "login" in lower_message or "登录" in status_message:
            raise LoginRequiredError(f"Douyin login is required: {status_message}")
        raise AccountEnumerationError(f"Douyin API error {status_code}: {status_message}")

    videos: list[AccountVideo] = []
    nickname = ""
    for index, item in enumerate(body.get("aweme_list") or []):
        video_id = str(item.get("aweme_id") or "")
        if not video_id:
            continue
        author = item.get("author") or {}
        nickname = nickname or str(author.get("nickname") or "")
        videos.append(AccountVideo(
            video_id=video_id,
            source_url=f"https://www.douyin.com/video/{video_id}",
            title=str(item.get("desc") or f"Douyin {video_id}"),
            published_at=int(item.get("create_time") or 0),
            duration_ms=int((item.get("video") or {}).get("duration") or 0),
            queue_position=index + 1,
        ))
    return EnumerationPage(
        videos=videos,
        cursor=str(body.get("max_cursor") or "0"),
        has_more=bool(body.get("has_more")),
        nickname=nickname,
    )


def enumerate_douyin_account(
    account_url: str,
    max_videos: int | None = None,
    reporter: StatusReporter | None = None,
    on_page: Callable[[EnumerationPage], None] | None = None,
    start_cursor: str = "0",
    known_video_ids: set[str] | None = None,
) -> tuple[str, list[AccountVideo], str, str, bool]:
    sec_uid = extract_sec_uid(account_url)
    if max_videos is not None and max_videos < 1:
        raise ValueError("--max-videos must be a positive integer")
    if reporter:
        reporter.stage("Opening Douyin account in logged-in browser")
    _run_opencli(["operate", "open", f"https://www.douyin.com/user/{sec_uid}"], timeout=60)

    cursor = start_cursor
    all_videos: list[AccountVideo] = []
    seen = set(known_video_ids or ())
    nickname = ""
    page_number = 0
    enumeration_complete = False
    while True:
        page_number += 1
        if reporter:
            reporter.stage("Enumerating Douyin account videos", detail=f"page {page_number}")
        request_cursor = cursor
        page = _fetch_page(sec_uid, request_cursor)
        nickname = nickname or page.nickname
        candidates = [video for video in page.videos if video.video_id not in seen]
        remaining = None if max_videos is None else max_videos - len(all_videos)
        page_truncated = remaining is not None and len(candidates) > remaining
        fresh = candidates if remaining is None else candidates[:max(0, remaining)]
        for video in fresh:
            seen.add(video.video_id)
            all_videos.append(video)
        stopped_by_limit = max_videos is not None and len(all_videos) >= max_videos
        resume_cursor = request_cursor if page_truncated else page.cursor
        if on_page:
            on_page(EnumerationPage(
                fresh,
                resume_cursor,
                page_truncated or page.has_more,
                page.nickname,
            ))
        if stopped_by_limit:
            cursor = resume_cursor
            enumeration_complete = not page.has_more and not page_truncated
            break
        if not page.has_more or page.cursor == request_cursor:
            enumeration_complete = not page.has_more
            cursor = page.cursor
            break
        cursor = page.cursor
    return sec_uid, all_videos, nickname, cursor, enumeration_complete
