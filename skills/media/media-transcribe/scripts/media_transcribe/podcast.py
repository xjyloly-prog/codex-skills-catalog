from __future__ import annotations

import html as html_lib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

from .status import StatusReporter

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
AUDIO_RE = re.compile(r"\.(mp3|m4a|wav|ogg|aac|flac)(?:\?|$)", re.IGNORECASE)
ITUNES_NS = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}


@dataclass(frozen=True)
class Episode:
    number: int
    title: str
    date: str
    duration: str
    duration_seconds: int
    audio_url: str


def fetch_text(url: str, timeout: int = 35) -> str:
    result = subprocess.run(
        ["curl", "-f", "-s", "-L", "--max-time", str(timeout - 5),
         "-H", f"User-Agent: {USER_AGENT}", url],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=True,
    )
    return result.stdout


def extract_audio_from_html(content: str, page_url: str) -> tuple[str, str]:
    title = "Podcast Episode"
    title_match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = html_lib.unescape(re.sub(r"<[^>]+>", "", title_match.group(1))).strip()
        title = re.sub(r"\s*[-|—].*$", "", title) or title

    patterns = [
        r'<meta[^>]+(?:property|name)=["\']og:audio["\'][^>]+content=["\'](.*?)["\']',
        r'<meta[^>]+content=["\'](.*?)["\'][^>]+(?:property|name)=["\']og:audio["\']',
        r'<audio[^>]+src=["\'](.*?)["\']',
        (r'["\'](?:audioUrl|mediaSrc|enclosure|url)["\']\s*:\s*["\']'
         r'(https?://[^"\']+\.(?:mp3|m4a|wav|ogg|aac|flac)[^"\']*)["\']'),
        r'(https?://[^\s"\'<>]+\.(?:mp3|m4a|wav|ogg|aac|flac)(?:\?[^\s"\'<>]*)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            value = html_lib.unescape(match.group(1)).replace(r"\/", "/")
            return urljoin(page_url, value), title
    raise RuntimeError(f"Cannot extract audio URL from page: {page_url}")


def audio_extension(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".mp3", ".m4a", ".wav", ".ogg", ".aac", ".flac"):
        if path.endswith(ext):
            return ext
    return ".m4a"


def download_url(url: str, destination: Path, timeout: int = 1900) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    partial.unlink(missing_ok=True)
    try:
        subprocess.run(
            ["curl", "-f", "-L", "-o", str(partial), "--max-time", str(timeout - 100),
             "-s", "-H", f"User-Agent: {USER_AGENT}", url],
            timeout=timeout,
            check=True,
        )
        if not partial.exists() or partial.stat().st_size < 10_000:
            raise RuntimeError("Downloaded file is too small and is probably not valid audio.")
        partial.replace(destination)
        return destination
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def acquire_podcast(
    source: str,
    temp_dir: Path,
    reporter: StatusReporter | None = None,
) -> tuple[Path, str]:
    local = Path(source).expanduser()
    if local.is_file():
        if reporter:
            reporter.stage("Using local audio")
        return local.resolve(), local.stem

    if AUDIO_RE.search(source):
        audio_url, title = source, Path(urlparse(source).path).stem or "Podcast Episode"
    else:
        if reporter:
            reporter.stage("Parsing podcast source")
        audio_url, title = extract_audio_from_html(fetch_text(source), source)
    path = temp_dir / f"audio{audio_extension(audio_url)}"
    if reporter:
        reporter.stage("Downloading podcast audio", detail=title[:60])
    return download_url(audio_url, path), title


def parse_duration(value: str) -> int:
    value = value.strip()
    if not value:
        return 0
    if value.isdigit():
        return int(value)
    parts = value.split(":")
    try:
        numbers = [int(part) for part in parts]
    except ValueError:
        return 0
    if len(numbers) == 2:
        return numbers[0] * 60 + numbers[1]
    if len(numbers) == 3:
        return numbers[0] * 3600 + numbers[1] * 60 + numbers[2]
    return 0


def _node_text(item: ET.Element, path: str, namespaces: dict[str, str] | None = None) -> str:
    node = item.find(path, namespaces or {})
    return (node.text or "").strip() if node is not None else ""


def parse_rss_xml(content: str) -> list[Episode]:
    root = ET.fromstring(content)
    episodes: list[Episode] = []
    for index, item in enumerate(root.findall(".//item"), 1):
        title = _node_text(item, "title") or f"Episode {index}"
        pub_date = _node_text(item, "pubDate")
        duration = _node_text(item, "itunes:duration", ITUNES_NS)
        ep_number = _node_text(item, "itunes:episode", ITUNES_NS)
        enclosure = item.find("enclosure")
        audio_url = html_lib.unescape(enclosure.get("url", "")) if enclosure is not None else ""
        if not audio_url:
            continue
        try:
            date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime("%Y-%m-%d")
        except ValueError:
            date = pub_date[:16]
        number = int(ep_number) if ep_number.isdigit() else index
        episodes.append(Episode(number, title, date, duration, parse_duration(duration), audio_url))
    return episodes


def parse_rss(url: str) -> list[Episode]:
    return parse_rss_xml(fetch_text(url))


def select_episodes(episodes: Iterable[Episode], start: int, count: int) -> list[Episode]:
    if start < 1 or count < 1:
        raise ValueError("--start and --count must be positive integers")
    end = start + count - 1
    return sorted(
        (episode for episode in episodes if start <= episode.number <= end),
        key=lambda episode: episode.number,
    )
