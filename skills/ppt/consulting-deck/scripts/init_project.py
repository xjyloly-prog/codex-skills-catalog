#!/usr/bin/env python3
"""Create a non-destructive consulting-deck project workspace."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DIRECTORIES = (
    "notes",
    "sources",
    "data",
    "assets",
    "src",
    "renders",
    "qa",
    "output",
)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", value)
    return value.strip("-") or "consulting-deck"


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a saved workspace for a Consulting Deck project."
    )
    parser.add_argument("project_dir", help="New, empty project directory")
    parser.add_argument("--title", default="", help="Working deck title")
    parser.add_argument("--language", default="zh-CN")
    parser.add_argument("--slides", type=int, default=10)
    parser.add_argument(
        "--density",
        choices=("speaker-led", "reading-first"),
        default="reading-first",
    )
    parser.add_argument(
        "--mode",
        choices=("research-analytical", "executive-story", "editorial-keynote"),
        default="executive-story",
    )
    parser.add_argument(
        "--analysis-route",
        choices=("source-synthesis", "problem-solving"),
        default="source-synthesis",
    )
    parser.add_argument(
        "--direction",
        choices=(
            "executive-classic",
            "swiss-analytical",
            "editorial-strategy",
            "research-analytical",
        ),
        default="executive-classic",
    )
    parser.add_argument("--brand", default="neutral")
    parser.add_argument(
        "--runtime",
        choices=("auto", "host-native", "ppt-master-adapter", "pptxgenjs"),
        default="auto",
    )
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    if root.exists() and any(root.iterdir()):
        parser.error(f"Refusing to write into non-empty directory: {root}")
    root.mkdir(parents=True, exist_ok=True)
    for name in DIRECTORIES:
        (root / name).mkdir(exist_ok=True)

    brief = {
        "project_id": slugify(args.title or root.name),
        "title": args.title,
        "audience": "",
        "decision": "",
        "analysis_route": args.analysis_route,
        "problem_statement": "",
        "in_scope": [],
        "out_of_scope": [],
        "context": "async",
        "deck_mode": args.mode,
        "density": args.density,
        "language": args.language,
        "aspect_ratio": "16:9",
        "target_slide_count": args.slides,
        "source_boundary": "",
        "freshness_requirement": "",
        "brand_profile": args.brand,
        "visual_direction": args.direction,
        "production_runtime": args.runtime,
        "compatibility_target": "Microsoft PowerPoint",
    }
    storyline = {
        "audience_question": "",
        "governing_thought": "",
        "narrative_spine": "",
        "supporting_arguments": [],
        "decision_or_action": "",
        "appendix_plan": [],
    }
    design_system = {
        "visual_direction": args.direction,
        "theme_asset": f"assets/themes/{args.direction}.json",
        "brand_profile": args.brand,
        "signature_device": "",
        "font_fallbacks": {},
        "approved_previews": [],
    }

    write_json(root / "brief.json", brief)
    write_json(root / "hypotheses.json", [])
    write_json(root / "evidence.json", [])
    write_json(root / "charts.json", [])
    write_json(root / "storyline.json", storyline)
    write_json(root / "design-system.json", design_system)
    write_json(root / "slides.json", [])
    write_json(
        root / "project-state.json",
        {
            "stage": "S1-contract",
            "completed_stages": [],
            "gate_files": {
                "project_validation": "qa/project-validation.json",
                "pptx_inspection": "qa/pptx-inspection.json",
                "final_gate": "qa/final-gate.json",
            },
            "last_updated": "",
        },
    )
    write_json(
        root / "qa" / "manual-review.json",
        {
            "evidence_reviewed": False,
            "storyline_reviewed": False,
            "charts_reviewed": False,
            "visual_reviewed": False,
            "coherence_reviewed": False,
            "compatibility_reviewed": False,
            "reviewer": "",
            "reviewed_at": "",
            "warnings_accepted": [],
            "notes": [],
        },
    )
    (root / "qa" / "experience-log.md").write_text(
        "# Repeatable production lessons\n\n",
        encoding="utf-8",
    )

    print(f"Created Consulting Deck workspace: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
