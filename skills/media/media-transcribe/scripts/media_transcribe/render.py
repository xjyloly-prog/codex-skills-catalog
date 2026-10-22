from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .models import Transcript

TAGS = {
    "douyin": "抖音",
    "bilibili": "B站",
    "tiktok": "TikTok",
    "weibo": "微博",
    "zhihu": "知乎",
    "youtube": "YouTube",
    "wechat-channels": "视频号",
    "podcast": "播客",
}

_TIMESTAMP_LINE = re.compile(
    r"^\[\s*\d+(?:\.\d+)?s\s*->\s*\d+(?:\.\d+)?s\]\s*(.*)$"
)
_SENTENCE_ENDINGS = ("。", "！", "？", "!", "?", "…", ".")


def normalize_transcript_text(platform: str, text: str) -> str:
    if platform == "podcast":
        return text
    lines = text.splitlines()
    if not any(_TIMESTAMP_LINE.match(line) for line in lines):
        return text
    raise RuntimeError(
        "Video transcript still contains timestamps. Run punctuation restoration before rendering."
    )


def yaml_scalar(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def sanitize_filename(title: str, fallback: str = "transcript", limit: int = 80) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)
    value = re.sub(r"\s+", "-", value).strip(" .-")
    return value[:limit] or fallback


def render_markdown(
    title: str,
    platform: str,
    source: str,
    transcript: Transcript,
    metadata: dict[str, str | int] | None = None,
) -> str:
    tag = TAGS.get(platform, platform)
    translated = transcript.translated_text is not None
    lines = [
        "---",
        f"title: {yaml_scalar(title)}",
        "type: note",
        f"tags: [{yaml_scalar(tag)}]",
        f"created: {date.today().isoformat()}",
        f"platform: {yaml_scalar(platform)}",
        f"source: {yaml_scalar(source)}",
        f"language: {yaml_scalar(transcript.language)}",
        f"translated: {'true' if translated else 'false'}",
        f"transcriber: {yaml_scalar(transcript.transcriber)}",
    ]
    for key, value in (metadata or {}).items():
        rendered = str(value) if isinstance(value, int) else yaml_scalar(str(value))
        lines.append(f"{key}: {rendered}")
    lines.extend([
        "---",
        "",
        f"# {title}",
        "",
        f"> 转录引擎：{transcript.transcriber} | 耗时：{transcript.elapsed:.0f}秒",
        "",
    ])
    if translated:
        lines.extend(["## 中文翻译", "", transcript.translated_text or "", "", "---", "",
                      "## English Original", "", transcript.text])
    else:
        lines.extend(["## Transcript", "", normalize_transcript_text(platform, transcript.text)])
    return "\n".join(lines).rstrip() + "\n"


def output_path(output_dir: Path, title: str, platform: str) -> Path:
    return output_dir / f"{sanitize_filename(title)}-{platform}.md"


def write_markdown(path: Path, content: str, overwrite: bool = False) -> Path:
    if path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {path}. Use --overwrite to replace it.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)
    return path
