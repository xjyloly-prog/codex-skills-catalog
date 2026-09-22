#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_POSITIVE_PROMPT_FIXTURE_TAGS = {
    "douyin", "douyin-account-batch", "bilibili", "tiktok", "weibo", "zhihu",
    "youtube", "wechat-channels", "podcast", "rss-download-only",
}
REQUIRED_NEGATIVE_PROMPT_FIXTURE_TAGS = {
    "account-launch", "publishing", "existing-markdown", "restricted",
    "learning-notes-downstream",
}


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "evals/evals.json").read_text(encoding="utf-8"))
    assert data["skill_name"] == "media-transcribe"
    assert data["evaluation_type"] == "static prompt-fixture coverage"
    assert "does not invoke a live host router" in data["limitations"]
    evals = data["evals"]
    ids = [item["id"] for item in evals]
    assert len(ids) == len(set(ids)), "duplicate eval id"
    positives = {tag for item in evals if item["route"] == "positive" for tag in item["tags"]}
    negatives = {tag for item in evals if item["route"] == "negative" for tag in item["tags"]}
    assert REQUIRED_POSITIVE_PROMPT_FIXTURE_TAGS <= positives, (
        "missing positive prompt fixture tags: "
        f"{REQUIRED_POSITIVE_PROMPT_FIXTURE_TAGS - positives}"
    )
    assert REQUIRED_NEGATIVE_PROMPT_FIXTURE_TAGS <= negatives, (
        "missing negative prompt fixture tags: "
        f"{REQUIRED_NEGATIVE_PROMPT_FIXTURE_TAGS - negatives}"
    )
    assert all(len(item["prompt"]) >= 20 and item["expected"] for item in evals)
    print("PASS: media-transcribe static prompt-fixture coverage "
          "(schema/tag check; not a live trigger evaluation)")


if __name__ == "__main__":
    main()
