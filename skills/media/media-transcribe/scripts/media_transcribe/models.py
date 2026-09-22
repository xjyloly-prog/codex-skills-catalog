from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class PlatformProfile:
    name: str
    tag: str
    language: str
    default_title: str
    user_agent: str
    referer: str
    extra_args: tuple[str, ...] = ()
    retries: int = 3
    download_timeout: int = 600


@dataclass
class MediaSource:
    platform: str
    source: str
    audio_path: Path
    title: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class Transcript:
    text: str
    language: str
    transcriber: str
    elapsed: float
    segments: list[str] = field(default_factory=list)
    translated_text: Optional[str] = None
