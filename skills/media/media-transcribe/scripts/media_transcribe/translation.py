from __future__ import annotations

import json
import os
import urllib.request

from .status import StatusReporter


def _chunks(text: str, limit: int = 3500) -> list[str]:
    if len(text) <= 4000:
        return [text]
    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        if current and len(current) + len(paragraph) + 2 > limit:
            chunks.append(current)
            current = ""
        if len(paragraph) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(paragraph[i:i + limit] for i in range(0, len(paragraph), limit))
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph
    if current:
        chunks.append(current)
    return [chunk for chunk in chunks if chunk]


def translate_with_deepseek(
    text: str,
    api_key: str | None = None,
    reporter: StatusReporter | None = None,
) -> str | None:
    key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        if reporter:
            reporter.warning("No DEEPSEEK_API_KEY; keeping the English transcript.")
        return None

    translated: list[str] = []
    chunks = _chunks(text)
    for index, chunk in enumerate(chunks, 1):
        if reporter:
            reporter.detail(f"chunk {index}/{len(chunks)}")
        payload = json.dumps({
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是专业翻译。将英文翻译成中文，保持原文风格和格式，不添加解释。"},
                {"role": "user", "content": chunk},
            ],
            "temperature": 0.3,
        }).encode("utf-8")
        request = urllib.request.Request(
            "https://api.deepseek.com/v1/chat/completions",
            data=payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = json.loads(response.read())
            translated.append(body["choices"][0]["message"]["content"])
        except Exception as exc:
            if reporter:
                reporter.warning(f"Translation failed; keeping original transcript: {exc}")
            return None
    return "\n\n".join(translated)
