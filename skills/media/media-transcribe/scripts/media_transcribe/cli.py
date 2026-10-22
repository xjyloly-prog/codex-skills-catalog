from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from .account_enumerator import enumerate_douyin_account, extract_sec_uid
from .account_queue import AccountQueue, QueueLockedError
from .account_worker import AccountWorker
from .dependencies import (
    dependency_spec_for_rss,
    dependency_spec_for_source,
    ensure_dependencies,
    ensure_opencli,
)
from .downloaders import PROFILES, acquire_douyin, acquire_wechat_channels, acquire_with_yt_dlp
from .engines import (
    load_sensevoice_model,
    load_whisper_model,
    paragraphize_video_text,
    restore_video_transcript_text,
    transcribe_sensevoice,
    transcribe_whisper,
)
from .models import MediaSource
from .podcast import acquire_podcast, audio_extension, download_url, parse_rss, select_episodes
from .render import output_path, render_markdown, sanitize_filename, write_markdown
from .routing import PLATFORMS, detect_platform
from .status import StatusReporter
from .translation import translate_with_deepseek


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="统一转录抖音、B站、TikTok、微博、知乎、YouTube、视频号、播客和本地音频"
    )
    parser.add_argument("source", nargs="?", help="平台 URL、BVID、播客页面、音频 URL 或本地音频")
    parser.add_argument("output_legacy", nargs="?", help=argparse.SUPPRESS)
    parser.add_argument("--rss-url", help="RSS feed URL；启用播客批量模式")
    parser.add_argument("--account-url", help="抖音账号 URL 或 sec_uid；启用持久队列模式")
    parser.add_argument("--sync-only", action="store_true", help="账号模式仅同步公开视频列表")
    parser.add_argument("--retry-failed", action="store_true", help="账号模式重新入队最终失败的视频")
    parser.add_argument("--max-videos", type=int, help="账号模式最多同步的视频数")
    parser.add_argument("--order", choices=("oldest", "newest"), default="oldest",
                        help="账号队列顺序（默认 oldest）")
    parser.add_argument("--request-delay", type=float, default=8.0,
                        help="账号视频之间的等待秒数（默认 8）")
    parser.add_argument("--output", "-o", dest="output", help="Markdown 输出目录（默认当前目录）")
    parser.add_argument("--platform", choices=PLATFORMS, default="auto", help="默认自动识别来源")
    parser.add_argument("--no-translate", action="store_true", help="关闭 YouTube 英文转中文")
    parser.add_argument(
        "--allow-third-party-resolver",
        action="store_true",
        help="允许将单个视频号分享链接提交给 sph.litao.workers.dev 解析",
    )
    parser.add_argument(
        "--allow-yuanbao-fallback",
        action="store_true",
        help=(
            "线上解析不可用时，允许打开临时隔离 Chrome 并等待用户手动登录腾讯元宝；"
            "不导出 Cookie、不修改系统代理"
        ),
    )
    parser.add_argument("--overwrite", action="store_true", help="覆盖已存在的 Markdown")
    parser.add_argument("--start", type=int, default=1, help="RSS 起始集号（按 itunes:episode，默认 1）")
    parser.add_argument("--count", type=int, default=10, help="RSS 处理数量（默认 10）")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--download-only", action="store_true", help="RSS 仅下载音频")
    mode.add_argument("--transcribe-only", action="store_true", help="RSS 仅转录已下载音频")
    return parser


def _output_dir(args: argparse.Namespace) -> Path:
    return Path(args.output or args.output_legacy or ".").expanduser().resolve()


def transcribe_one(args: argparse.Namespace, reporter: StatusReporter) -> Path:
    if not args.source:
        raise ValueError("source is required unless --rss-url is used")
    reporter.stage("Detecting source")
    platform = detect_platform(args.source, args.platform)
    if platform == "wechat-channels" and not args.allow_third_party_resolver:
        raise RuntimeError(
            "WeChat Channels transcription sends the share URL to a third-party resolver. "
            "Rerun with --allow-third-party-resolver after confirming this disclosure."
        )
    local_audio = platform == "podcast" and Path(args.source).expanduser().is_file()
    if platform == "wechat-channels":
        reporter.set_total(13 if args.allow_yuanbao_fallback else 10)
    elif platform == "douyin":
        reporter.set_total(10)
    else:
        reporter.set_total(8 if not local_audio else 6)
    reporter.stage("Checking dependencies")
    ensure_dependencies(dependency_spec_for_source(platform, args.source))
    output_dir = _output_dir(args)
    temp_dir = Path(tempfile.mkdtemp(prefix=f"media-transcribe-{platform}-"))
    try:
        if platform == "podcast":
            audio_path, title = acquire_podcast(args.source, temp_dir, reporter)
            media = MediaSource(platform, args.source, audio_path, title)
            reporter.stage("Download complete; preparing transcription")
            reporter.stage("Loading faster-whisper small")
            model = load_whisper_model()
            reporter.stage("Transcribing audio")
            with reporter.heartbeat("Transcription in progress"):
                transcript = transcribe_whisper(str(media.audio_path), model=model)
        else:
            if platform == "douyin":
                media = acquire_douyin(args.source, temp_dir, reporter)
            elif platform == "wechat-channels":
                media = acquire_wechat_channels(
                    args.source,
                    temp_dir,
                    reporter,
                    consent=args.allow_third_party_resolver,
                    yuanbao_fallback=args.allow_yuanbao_fallback,
                )
            else:
                media = acquire_with_yt_dlp(platform, args.source, temp_dir, reporter)
            language = "zh" if platform in ("douyin", "wechat-channels") else PROFILES[platform].language
            reporter.stage("Download complete; preparing transcription")
            reporter.stage("Loading SenseVoice-Small")
            library_stdout = io.StringIO()
            library_stderr = io.StringIO()
            with contextlib.redirect_stdout(library_stdout), contextlib.redirect_stderr(library_stderr):
                model = load_sensevoice_model()
            reporter.forward(library_stdout.getvalue())
            reporter.forward(library_stderr.getvalue())
            reporter.stage("Transcribing audio")
            with reporter.heartbeat("Transcription in progress"):
                transcript = transcribe_sensevoice(
                    str(media.audio_path), language, model=model, reporter=reporter,
                )
            if platform == "youtube" and transcript.language == "en" and not args.no_translate:
                if os.environ.get("DEEPSEEK_API_KEY"):
                    reporter.extend_total(1)
                    reporter.stage("Translating transcript")
                transcript.translated_text = translate_with_deepseek(transcript.text, reporter=reporter)

        if platform != "podcast" and transcript.transcriber == "faster-whisper-small":
            reporter.stage("Restoring video punctuation and paragraphs")
            with reporter.heartbeat("Video transcript normalization in progress"):
                transcript.text = restore_video_transcript_text(transcript.text)
        elif platform != "podcast":
            transcript.text = paragraphize_video_text(transcript.text)

        reporter.stage("Writing Markdown")
        path = output_path(output_dir, media.title, platform)
        content = render_markdown(media.title, platform, media.source, transcript, media.metadata)
        return write_markdown(path, content, args.overwrite)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def transcribe_rss(args: argparse.Namespace, reporter: StatusReporter) -> list[Path]:
    reporter.stage("Checking RSS dependencies")
    ensure_dependencies(dependency_spec_for_rss(args.download_only, args.transcribe_only))
    reporter.stage("Fetching RSS feed")
    episodes = select_episodes(parse_rss(args.rss_url), args.start, args.count)
    reporter.set_total(2 + len(episodes))
    reporter.detail(f"selected {len(episodes)} episode(s)")

    output_dir = _output_dir(args)
    audio_dir = output_dir / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_dir.mkdir(parents=True, exist_ok=True)
    prepared: list[tuple[object, Path, Path, str]] = []
    outputs: list[Path] = []

    for index, episode in enumerate(episodes, 1):
        prefix = f"Episode {index}/{len(episodes)} · EP{episode.number:03d}"
        base = f"EP{episode.number:03d}-{sanitize_filename(episode.title)}"
        transcript_path = output_dir / f"{base}-podcast.md"
        if (not args.download_only and transcript_path.exists()
                and transcript_path.stat().st_size > 500 and not args.overwrite):
            reporter.stage(f"{prefix}: Reusing transcript")
            outputs.append(transcript_path)
            continue

        audio_path = audio_dir / f"{base}{audio_extension(episode.audio_url)}"
        if not args.transcribe_only:
            if audio_path.is_file() and audio_path.stat().st_size >= 10_000:
                reporter.stage(f"{prefix}: Reusing audio")
            else:
                reporter.stage(f"{prefix}: Downloading audio")
                try:
                    download_url(episode.audio_url, audio_path)
                except (RuntimeError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                    reporter.warning(f"{prefix} download failed, skipped: {exc}")
                    continue
        else:
            reporter.stage(f"{prefix}: Locating downloaded audio")

        if audio_path.is_file() and audio_path.stat().st_size >= 10_000:
            prepared.append((episode, audio_path, transcript_path, prefix))
        elif not args.download_only:
            reporter.warning(f"{prefix} audio missing or invalid, skipped: {audio_path}")

    if args.download_only:
        return []

    if prepared:
        reporter.extend_total(2 + len(prepared) * 2)
        reporter.stage("Download complete; preparing transcription")
        reporter.stage("Loading faster-whisper small")
        model = load_whisper_model()
    else:
        model = None

    for episode, audio_path, path, prefix in prepared:
        reporter.stage(f"{prefix}: Transcribing")
        try:
            with reporter.heartbeat(f"{prefix}: Transcription in progress"):
                transcript = transcribe_whisper(str(audio_path), model=model)
            reporter.stage(f"{prefix}: Writing Markdown")
            content = render_markdown(episode.title, "podcast", episode.audio_url, transcript)
            outputs.append(write_markdown(path, content, args.overwrite))
        except Exception as exc:
            reporter.warning(f"{prefix} transcription failed, skipped: {exc}")
    return outputs


def transcribe_account(args: argparse.Namespace, reporter: StatusReporter) -> list[Path]:
    reporter.stage("Checking account dependencies")
    ensure_opencli()
    if not args.sync_only:
        ensure_dependencies(dependency_spec_for_source("douyin", args.account_url))

    sec_uid = extract_sec_uid(args.account_url)
    output_root = _output_dir(args) / "accounts"
    account_dir = output_root / sanitize_filename(sec_uid, fallback="douyin-account")
    queue_path = account_dir / "queue.sqlite3"
    with AccountQueue(queue_path) as queue:
        existing_account = queue.account(sec_uid)
        if existing_account is None:
            queue.upsert_account(sec_uid, args.account_url, args.order)
            start_cursor = "0"
        else:
            start_cursor = (
                existing_account["last_cursor"]
                if not existing_account["enumeration_complete"]
                else "0"
            )
        known_video_ids = queue.video_ids(sec_uid)

        def persist_page(page) -> None:
            queue.add_videos(sec_uid, page.videos)
            queue.upsert_account(
                sec_uid, args.account_url, args.order, page.nickname, page.cursor, not page.has_more,
            )

        synced_uid, videos, nickname, cursor, complete = enumerate_douyin_account(
            args.account_url,
            max_videos=args.max_videos,
            reporter=reporter,
            on_page=persist_page,
            start_cursor=start_cursor,
            known_video_ids=known_video_ids,
        )
        queue.add_videos(synced_uid, videos)
        queue.upsert_account(synced_uid, args.account_url, args.order, nickname, cursor, complete)
        queue.reorder(synced_uid, args.order)
        if args.retry_failed:
            queue.retry_failed(synced_uid)
        worker = AccountWorker(
            queue,
            synced_uid,
            account_dir,
            reporter,
            request_delay=args.request_delay,
        )
        if args.sync_only:
            worker.write_summary()
            return []
        return worker.run()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    modes = sum(bool(value) for value in (args.source, args.rss_url, args.account_url))
    if modes > 1:
        parser.error("source, --rss-url, and --account-url are mutually exclusive")
    if modes == 0:
        parser.error("provide source, --rss-url, or --account-url")
    if not args.rss_url and (args.download_only or args.transcribe_only):
        parser.error("--download-only/--transcribe-only require --rss-url")
    if not args.account_url and (
        args.sync_only or args.retry_failed or args.max_videos is not None
        or args.order != "oldest" or args.request_delay != 8.0
    ):
        parser.error(
            "--sync-only/--retry-failed/--max-videos/--order/--request-delay require --account-url"
        )
    wechat_flags = args.allow_third_party_resolver or args.allow_yuanbao_fallback
    if wechat_flags:
        if not args.source:
            parser.error(
                "--allow-third-party-resolver/--allow-yuanbao-fallback require a "
                "WeChat Channels positional source"
            )
        try:
            source_platform = detect_platform(args.source, args.platform)
        except ValueError as exc:
            parser.error(str(exc))
        if source_platform != "wechat-channels":
            parser.error(
                "--allow-third-party-resolver/--allow-yuanbao-fallback are only valid "
                "for a WeChat Channels share URL"
            )
    if args.allow_yuanbao_fallback and not args.allow_third_party_resolver:
        parser.error(
            "--allow-yuanbao-fallback requires --allow-third-party-resolver because the "
            "public resolver is always attempted first"
        )
    if args.request_delay < 0:
        parser.error("--request-delay cannot be negative")

    try:
        with StatusReporter() as reporter:
            if args.account_url:
                paths = transcribe_account(args, reporter)
            elif args.rss_url:
                paths = transcribe_rss(args, reporter)
            else:
                paths = [transcribe_one(args, reporter)]
        for path in paths:
            print(path)
        return 0
    except (ValueError, RuntimeError, QueueLockedError, FileExistsError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired, json.JSONDecodeError, ET.ParseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"error: missing command or file: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
