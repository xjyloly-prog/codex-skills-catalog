from __future__ import annotations

import json
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from .models import MediaSource, PlatformProfile
from .status import StatusReporter

DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)
WECHAT_CHANNELS_RESOLVER = "https://sph.litao.workers.dev/api/fetch_video_profile"


class WechatResolverError(RuntimeError):
    pass


class WechatResolverUnavailableError(WechatResolverError):
    pass

PROFILES = {
    "bilibili": PlatformProfile("bilibili", "B站", "zh", "B站视频", DESKTOP_UA,
                                 "https://www.bilibili.com/", retries=1),
    "tiktok": PlatformProfile("tiktok", "TikTok", "auto", "TikTok Video", DESKTOP_UA,
                               "https://www.tiktok.com/", ("--geo-bypass",)),
    "weibo": PlatformProfile("weibo", "微博", "zh", "微博视频", MOBILE_UA,
                              "https://weibo.com/"),
    "zhihu": PlatformProfile("zhihu", "知乎", "zh", "知乎视频", DESKTOP_UA,
                              "https://www.zhihu.com/"),
    "youtube": PlatformProfile("youtube", "YouTube", "auto", "YouTube Video", DESKTOP_UA,
                                "https://www.youtube.com/", retries=1),
}


PROGRESS_PREFIX = "MT_PROGRESS|"
PROGRESS_TEMPLATE = (
    "download:MT_PROGRESS|%(progress.status)s|%(progress.downloaded_bytes)s|"
    "%(progress.total_bytes)s|%(progress.total_bytes_estimate)s|%(progress.speed)s|"
    "%(progress.eta)s"
)


@dataclass(frozen=True)
class DownloadProgress:
    percent: float | None
    text: str


def _yt_dlp_command(
    profile: PlatformProfile,
    args: list[str],
    *,
    show_progress: bool = False,
) -> list[str]:
    progress_args = (
        ["--progress", "--newline", "--progress-template", PROGRESS_TEMPLATE]
        if show_progress else ["--no-progress"]
    )
    return [
        sys.executable, "-m", "yt_dlp", "--no-check-certificates", *progress_args,
        "--user-agent", profile.user_agent, "--referer", profile.referer,
        *profile.extra_args, *args,
    ]


def run_yt_dlp(profile: PlatformProfile, args: list[str], timeout: int):
    return subprocess.run(
        _yt_dlp_command(profile, args),
        capture_output=True, text=True, timeout=timeout, check=True,
    )


def _value(value: str) -> float | None:
    if value in ("", "NA", "None"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _format_bytes(value: float) -> str:
    units = ("B", "KiB", "MiB", "GiB")
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def _format_eta(value: float) -> str:
    seconds = max(0, int(value))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


def _parse_progress_line(line: str) -> DownloadProgress | None:
    if not line.startswith(PROGRESS_PREFIX):
        return None
    parts = line.strip().split("|")
    if len(parts) != 7:
        return None
    _, status, downloaded_raw, total_raw, estimated_raw, speed_raw, eta_raw = parts
    downloaded = _value(downloaded_raw) or 0
    total = _value(total_raw)
    estimated = _value(estimated_raw)
    denominator = total or estimated
    percent = min(downloaded / denominator * 100, 100) if denominator else None
    details = []
    if percent is not None:
        details.append(f"{percent:.1f}%")
    if denominator:
        approximate = "~" if total is None and estimated is not None else ""
        downloaded_text = _format_bytes(downloaded).rsplit(" ", 1)[0]
        details.append(f"{downloaded_text}/{approximate}{_format_bytes(denominator)}")
    elif downloaded:
        details.append(_format_bytes(downloaded))
    speed = _value(speed_raw)
    if speed:
        details.append(f"{_format_bytes(speed)}/s")
    eta = _value(eta_raw)
    if eta is not None:
        details.append(f"ETA {_format_eta(eta)}")
    if status == "finished" and not details:
        details.append("download complete")
    return DownloadProgress(percent, " · ".join(details) or status)


def run_yt_dlp_with_progress(
    profile: PlatformProfile,
    args: list[str],
    timeout: int,
    reporter: StatusReporter | None,
) -> None:
    command = _yt_dlp_command(profile, args, show_progress=True)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stderr_lines: list[str] = []

    def read_stdout() -> None:
        assert process.stdout is not None
        for raw_line in process.stdout:
            parsed = _parse_progress_line(raw_line.rstrip("\r\n"))
            if parsed and reporter:
                reporter.progress(parsed.text, parsed.percent)

    def read_stderr() -> None:
        assert process.stderr is not None
        for raw_line in process.stderr:
            line = raw_line.rstrip("\r\n")
            if line.strip():
                stderr_lines.append(line.strip())

    stdout_reader = threading.Thread(target=read_stdout, daemon=True)
    stderr_reader = threading.Thread(target=read_stderr, daemon=True)
    stdout_reader.start()
    stderr_reader.start()
    try:
        return_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        process.kill()
        stdout_reader.join(timeout=1)
        stderr_reader.join(timeout=1)
        raise
    stdout_reader.join(timeout=1)
    stderr_reader.join(timeout=1)
    if return_code:
        raise subprocess.CalledProcessError(
            return_code,
            command,
            stderr="\n".join(stderr_lines[-20:]),
        )


def normalize_wechat_channels_url(source: str) -> str:
    value = source.strip().strip("<>[](){}\"'")
    parsed = urlsplit(value)
    if parsed.scheme.lower() != "https":
        raise ValueError("WeChat Channels share URL must use HTTPS.")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("WeChat Channels share URL must not contain credentials or a custom port.")
    if (parsed.hostname or "").lower() != "weixin.qq.com":
        raise ValueError("Expected a weixin.qq.com WeChat Channels share URL.")
    if not re.fullmatch(r"/sph/[^/]+/?", parsed.path):
        raise ValueError("Expected one /sph/<token> WeChat Channels share URL.")
    path = parsed.path.rstrip("/")
    return urlunsplit(("https", "weixin.qq.com", path, parsed.query, ""))


def resolver_error_message(detail: object, status: int) -> str:
    clean = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(detail or ""))
    if re.search(r"(?:http\s*)?401\b|unauthori[sz]ed", clean, re.IGNORECASE):
        return (
            "WeChat Channels resolver credentials are unavailable or expired. "
            "The third-party service must refresh them; try again later."
        )
    return f"WeChat Channels resolver failed: {clean or f'HTTP {status}'}"


def request_json(url: str, payload: dict, timeout: int = 45) -> dict:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "media-transcribe/2.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            detail = None
        raise WechatResolverUnavailableError(resolver_error_message(detail, exc.code)) from exc
    except urllib.error.URLError as exc:
        reason = _safe_remote_text(exc.reason)
        raise WechatResolverUnavailableError(
            f"WeChat Channels resolver request failed: {reason}"
        ) from exc
    except TimeoutError as exc:
        raise WechatResolverUnavailableError(
            "WeChat Channels resolver request timed out."
        ) from exc
    try:
        result = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WechatResolverUnavailableError(
            "WeChat Channels resolver returned invalid JSON."
        ) from exc
    if not isinstance(result, dict):
        raise WechatResolverUnavailableError(
            "WeChat Channels resolver returned an unexpected response."
        )
    return result


def _trusted_wechat_media_url(value: str) -> str:
    parsed = urlsplit(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme.lower() != "https" or not _host_matches(host, "video.qq.com"):
        raise RuntimeError(f"WeChat Channels resolver returned an unexpected host: {host or 'missing'}")
    if parsed.username or parsed.password or parsed.port:
        raise RuntimeError("WeChat Channels media URL contains credentials or a custom port.")
    return value


def _host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def _safe_remote_text(value: object) -> str:
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", str(value))


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, _req, _fp, _code, _msg, _headers, _newurl):
        return None


def download_wechat_media(url: str, destination: Path, timeout: int = 900) -> None:
    opener = urllib.request.build_opener(_NoRedirect)
    current = _trusted_wechat_media_url(url)
    for _ in range(6):
        request = urllib.request.Request(current, headers={"User-Agent": DESKTOP_UA})
        try:
            with opener.open(request, timeout=timeout) as response, destination.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    output.write(chunk)
                return
        except urllib.error.HTTPError as exc:
            if exc.code not in (301, 302, 303, 307, 308):
                raise RuntimeError(f"WeChat Channels media download failed: HTTP {exc.code}") from exc
            location = exc.headers.get("Location")
            if not location:
                raise RuntimeError("WeChat Channels media redirect is missing a destination.") from exc
            current = _trusted_wechat_media_url(urljoin(current, location))
    raise RuntimeError("WeChat Channels media download exceeded the redirect limit.")


def parse_wechat_channels_profile(profile: dict) -> tuple[str, str, dict[str, str]]:
    if profile.get("errCode") not in (None, 0):
        detail = _safe_remote_text(profile.get("errMsg") or profile["errCode"])
        raise WechatResolverUnavailableError(f"WeChat Channels resolver failed: {detail}")
    data = profile.get("data")
    if not isinstance(data, dict) or not isinstance(data.get("feedInfo"), dict):
        raise WechatResolverUnavailableError(
            "WeChat Channels resolver response is missing feed information."
        )
    feed = data["feedInfo"]
    candidates = (
        (feed.get("h264VideoInfo") or {}).get("videoUrl"),
        (feed.get("h265VideoInfo") or {}).get("videoUrl"),
        feed.get("videoUrl"),
    )
    media_url = next((value for value in candidates if isinstance(value, str) and value), None)
    if not media_url:
        raise WechatResolverUnavailableError(
            "WeChat Channels resolver returned no downloadable video URL."
        )
    media_url = _trusted_wechat_media_url(media_url)
    description = feed.get("description") if isinstance(feed.get("description"), str) else ""
    title = next((line.strip() for line in description.splitlines() if line.strip()), "视频号视频")
    author = data.get("authorInfo") or {}
    metadata = {}
    if isinstance(author.get("nickname"), str) and author["nickname"].strip():
        metadata["author"] = author["nickname"].strip()
    if isinstance(feed.get("createtime"), int):
        metadata["published_at"] = str(feed["createtime"])
    return title, media_url, metadata


def _probe_wechat_video(video_path: Path) -> None:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-show_entries", "stream=codec_type", "-of", "json", str(video_path)],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    try:
        probe = json.loads(result.stdout)
        duration = float(probe["format"]["duration"])
        stream_types = {stream.get("codec_type") for stream in probe.get("streams", [])}
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise RuntimeError("Downloaded WeChat Channels video failed media validation.") from exc
    if duration <= 0 or "video" not in stream_types or "audio" not in stream_types:
        raise RuntimeError("Downloaded WeChat Channels media must contain video, audio, and positive duration.")


def prepare_wechat_media(
    source: str,
    title: str,
    media_url: str,
    metadata: dict[str, str],
    temp_dir: Path,
    reporter: StatusReporter | None = None,
) -> MediaSource:
    media_url = _trusted_wechat_media_url(media_url)
    video_path = temp_dir / "source.mp4"
    audio_path = temp_dir / "audio.mp3"
    if reporter:
        reporter.stage("Downloading temporary WeChat Channels video")
    download_wechat_media(media_url, video_path)
    if not video_path.is_file() or video_path.stat().st_size < 10_000:
        raise RuntimeError("Downloaded WeChat Channels video is missing or too small.")
    if reporter:
        reporter.stage("Validating temporary WeChat Channels video")
    _probe_wechat_video(video_path)
    if reporter:
        reporter.stage("Extracting temporary audio")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "libmp3lame",
         "-ab", "128k", str(audio_path)],
        capture_output=True,
        timeout=300,
        check=True,
    )
    if not audio_path.is_file() or audio_path.stat().st_size < 10_000:
        raise RuntimeError("WeChat Channels audio extraction produced no usable audio.")
    return MediaSource("wechat-channels", source, audio_path, title, metadata)


def acquire_wechat_channels(
    source: str,
    temp_dir: Path,
    reporter: StatusReporter | None = None,
    *,
    consent: bool,
    yuanbao_fallback: bool = False,
) -> MediaSource:
    if not consent:
        raise RuntimeError(
            "WeChat Channels transcription sends the share URL to a third-party resolver. "
            "Rerun with --allow-third-party-resolver after confirming this disclosure."
        )
    normalized = normalize_wechat_channels_url(source)
    try:
        if reporter:
            reporter.stage("Resolving WeChat Channels share link")
        profile = request_json(WECHAT_CHANNELS_RESOLVER, {"url": normalized})
        title, media_url, metadata = parse_wechat_channels_profile(profile)
    except WechatResolverUnavailableError as exc:
        if not yuanbao_fallback:
            raise WechatResolverUnavailableError(
                f"{exc} To use the isolated Tencent Yuanbao fallback, rerun with "
                "--allow-yuanbao-fallback. It opens a temporary Chrome profile for manual login, "
                "does not export cookies, and does not change the system proxy."
            ) from exc
        if reporter:
            reporter.warning(f"Public resolver unavailable: {exc}")
        from .wechat_yuanbao import resolve_via_yuanbao

        result = resolve_via_yuanbao(normalized, temp_dir, reporter)
        title, media_url, metadata = result.title, result.media_url, result.metadata
    return prepare_wechat_media(normalized, title, media_url, metadata, temp_dir, reporter)


def normalize_bilibili_source(source: str) -> str:
    match = re.search(r"(BV[0-9A-Za-z]+)", source, re.IGNORECASE)
    if match:
        return f"https://www.bilibili.com/video/{match.group(1)}"
    return source


def acquire_with_yt_dlp(
    platform: str,
    source: str,
    temp_dir: Path,
    reporter: StatusReporter | None = None,
) -> MediaSource:
    profile = PROFILES[platform]
    resolved = normalize_bilibili_source(source) if platform == "bilibili" else source
    if reporter:
        reporter.stage(f"Resolving {profile.name} metadata")
    try:
        result = run_yt_dlp(profile, ["--get-title", resolved], 60)
        title = result.stdout.strip() or profile.default_title
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        title = profile.default_title

    audio_path = temp_dir / "audio.mp3"
    last_error: Exception | None = None
    for attempt in range(1, profile.retries + 1):
        try:
            if reporter:
                reporter.stage(f"Downloading and extracting {profile.name} audio", detail=f"attempt {attempt}/{profile.retries}")
            run_yt_dlp_with_progress(
                profile,
                ["--no-playlist", "--extract-audio", "--audio-format", "mp3", "--audio-quality", "128K",
                 "-o", str(audio_path), resolved],
                profile.download_timeout,
                reporter,
            )
            if not audio_path.exists() or audio_path.stat().st_size < 10_000:
                raise RuntimeError("Downloaded audio is missing or too small.")
            return MediaSource(platform, source, audio_path, title)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, RuntimeError) as exc:
            last_error = exc
            if attempt < profile.retries:
                time.sleep(2 * attempt)
    raise RuntimeError(f"{profile.name} audio download failed: {last_error}")


def extract_douyin_video_id(source: str) -> str:
    url = source
    if "v.douyin.com" in source:
        result = subprocess.run(
            ["curl", "-f", "-sI", "-L", "-H", f"User-Agent: {MOBILE_UA}", source],
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
        locations = [line.split(":", 1)[1].strip() for line in result.stdout.splitlines()
                     if line.lower().startswith("location:")]
        if locations:
            url = locations[-1]
    match = re.search(r"/video/(\d+)", url)
    if not match:
        raise ValueError(f"Cannot extract Douyin video id from: {source}")
    return match.group(1)


def parse_douyin_router_data(content: str) -> tuple[str, str]:
    match = re.search(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", content, re.DOTALL)
    if not match:
        raise RuntimeError("Douyin _ROUTER_DATA was not found.")
    raw = match.group(1).strip().removesuffix(";").strip()
    try:
        data = json.loads(raw)
        item = data["loaderData"]["video_(id)/page"]["videoInfoRes"]["item_list"][0]
        title = item.get("desc") or "抖音视频"
        video_url = item["video"]["play_addr"]["url_list"][0].replace("playwm", "play")
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Douyin page data has an unexpected shape: {exc}") from exc
    return title, video_url


def acquire_douyin(
    source: str,
    temp_dir: Path,
    reporter: StatusReporter | None = None,
) -> MediaSource:
    if reporter:
        reporter.stage("Resolving Douyin short link")
    video_id = extract_douyin_video_id(source)
    share_url = f"https://www.iesdouyin.com/share/video/{video_id}"
    if reporter:
        reporter.stage("Parsing Douyin metadata")
    page = subprocess.run(
        ["curl", "-f", "-s", "-L", "-H", f"User-Agent: {MOBILE_UA}", share_url],
        capture_output=True,
        text=True,
        timeout=35,
        check=True,
    ).stdout
    title, video_url = parse_douyin_router_data(page)
    video_path = temp_dir / f"{video_id}.mp4"
    audio_path = temp_dir / f"{video_id}.mp3"
    if reporter:
        reporter.stage("Downloading Douyin video")
    subprocess.run(
        ["curl", "-f", "-s", "-L", "-o", str(video_path),
         "-H", f"User-Agent: {MOBILE_UA}", "-H", "Referer: https://www.douyin.com/", video_url],
        timeout=300,
        check=True,
    )
    if reporter:
        reporter.stage("Extracting Douyin audio")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "libmp3lame",
         "-ab", "128k", str(audio_path)],
        capture_output=True,
        timeout=120,
        check=True,
    )
    video_path.unlink(missing_ok=True)
    if not audio_path.exists() or audio_path.stat().st_size < 10_000:
        raise RuntimeError("Douyin audio extraction produced no usable audio.")
    return MediaSource("douyin", source, audio_path, title)
