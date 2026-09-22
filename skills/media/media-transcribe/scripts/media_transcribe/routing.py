from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

PLATFORMS = (
    "auto",
    "douyin",
    "bilibili",
    "tiktok",
    "weibo",
    "zhihu",
    "youtube",
    "wechat-channels",
    "podcast",
)

_AUDIO_EXTENSIONS = (".mp3", ".m4a", ".wav", ".ogg", ".aac", ".flac")


def _host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def detect_platform(source: str, explicit: str = "auto") -> str:
    if explicit not in PLATFORMS:
        raise ValueError(f"Unsupported platform: {explicit}")
    if explicit != "auto":
        return explicit

    source = source.strip().strip("<>[](){}\"'")
    local = Path(source).expanduser()
    if local.is_file():
        if local.suffix.lower() not in _AUDIO_EXTENSIONS:
            raise ValueError(f"Local input is not a supported audio file: {local}")
        return "podcast"
    if re.fullmatch(r"BV[0-9A-Za-z]+", source, re.IGNORECASE):
        return "bilibili"

    parsed = urlparse(source)
    try:
        parsed_port = parsed.port
    except ValueError:
        parsed_port = -1
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    url_lower = source.lower()
    if not host:
        raise ValueError("Cannot identify source. Pass a URL, BV id, local audio file, or --platform.")

    if host == "youtu.be" or _host_matches(host, "youtube.com"):
        return "youtube"
    if (
        parsed.scheme.lower() == "https"
        and host == "weixin.qq.com"
        and not parsed.username
        and not parsed.password
        and parsed_port is None
        and re.fullmatch(r"/sph/[^/]+/?", parsed.path)
    ):
        return "wechat-channels"
    if _host_matches(host, "douyin.com") or _host_matches(host, "iesdouyin.com"):
        return "douyin"
    if _host_matches(host, "bilibili.com") or host == "b23.tv":
        return "bilibili"
    if _host_matches(host, "tiktok.com"):
        return "tiktok"
    if _host_matches(host, "weibo.com") or _host_matches(host, "weibo.cn"):
        return "weibo"
    if _host_matches(host, "zhihu.com"):
        return "zhihu"
    if _host_matches(host, "xiaoyuzhoufm.com") or _host_matches(host, "ximalaya.com"):
        return "podcast"
    if any(ext in url_lower for ext in _AUDIO_EXTENSIONS):
        return "podcast"

    raise ValueError(
        f"Cannot identify platform for {host}. Pass --platform podcast for an audio page, "
        "or choose the matching supported platform explicitly."
    )
