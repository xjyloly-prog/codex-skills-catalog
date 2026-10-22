#!/usr/bin/env python3
"""Create the final machine-readable delivery decision for a deck workspace."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from exhibit_contracts import ContractError, file_hash, local_path


REQUIRED_MANUAL_CHECKS = (
    "evidence_reviewed",
    "storyline_reviewed",
    "charts_reviewed",
    "visual_reviewed",
    "coherence_reviewed",
    "compatibility_reviewed",
)


def load_json(path: Path, blockers: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        blockers.append(f"Missing gate input: {path.name}")
    except json.JSONDecodeError as exc:
        blockers.append(f"Invalid JSON in {path.name}: {exc}")
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir")
    parser.add_argument(
        "--output",
        help="Defaults to <project_dir>/qa/final-gate.json",
    )
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    qa_dir = root / "qa"
    blockers: list[str] = []
    warnings: list[str] = []

    project = load_json(qa_dir / "project-validation.json", blockers)
    pptx = load_json(qa_dir / "pptx-inspection.json", blockers)
    manual = load_json(qa_dir / "manual-review.json", blockers)

    if not isinstance(project, dict) or not project:
        blockers.append("Project validation is empty or malformed")
        project = {}
    if not isinstance(pptx, dict) or not pptx:
        blockers.append("PPTX inspection is empty or malformed")
        pptx = {}
    if not isinstance(manual, dict) or not manual:
        blockers.append("Manual review is empty or malformed")
        manual = {}

    for label, report in (("Project validation", project), ("PPTX inspection", pptx)):
        for field in ("blockers", "warnings"):
            values = report.get(field, [])
            if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
                blockers.append(f"{label}: {field} must be a list of strings")
                report[field] = []
        if report.get("status") in {"passed", "passed_with_warnings"} and report.get("blockers"):
            blockers.append(f"{label}: passing status contradicts blockers")

    if project.get("status") == "failed":
        blockers.append("Project validation reports failure")
        blockers.extend(
            f"Project validation: {message}"
            for message in project.get("blockers", [])
        )
    elif project.get("status") not in {"passed", "passed_with_warnings"}:
        blockers.append("Project validation has no recognized passing status")

    if pptx.get("status") == "failed":
        blockers.append("PPTX inspection reports failure")
        blockers.extend(
            f"PPTX inspection: {message}"
            for message in pptx.get("blockers", [])
        )
    elif pptx.get("status") not in {"passed", "passed_with_warnings"}:
        blockers.append("PPTX inspection has no recognized passing status")

    brief = load_json(root / "brief.json", blockers)
    if isinstance(brief, dict) and brief.get("native_component_contract") == 1:
        charts = load_json(qa_dir / "chart-validation.json", blockers)
        if not isinstance(charts, dict) or charts.get("passed") is not True or charts.get("status") != "passed" or charts.get("blockers"):
            blockers.append("Actual chart data reconciliation missing or failed")
            charts = charts if isinstance(charts, dict) else {}
        if not charts.get("charts"):
            blockers.append("Chart reconciliation verified no charts")
        if not charts.get("source_hashes"):
            blockers.append("Chart reconciliation has no source lineage")
        if not project.get("source_hashes"):
            blockers.append("Project validation has no source lineage")
        for label, report in (("Chart reconciliation", charts), ("Project validation", project)):
            hashes = report.get("source_hashes", {})
            if not isinstance(hashes, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k,v in hashes.items()):
                blockers.append(f"{label}: source_hashes must map local paths to hashes")
                report["source_hashes"] = {}
        verified = charts.get("charts", [])
        if not isinstance(verified, list) or any(not isinstance(c, dict) or c.get("status") != "passed" or c.get("source_cache_reconciled") is not True or c.get("workbook_reconciled") is not True for c in verified):
            blockers.append("Native component charts lack complete cache/workbook verification")
        elif len(verified) != pptx.get("native_chart_count"):
            blockers.append("Chart reconciliation does not cover the inspected native chart count")
        for name, digest in charts.get("source_hashes", {}).items():
            try:
                if file_hash(local_path(root, name)) != digest:
                    blockers.append(f"Chart validation stale after input change: {name}")
            except (OSError, ContractError) as exc:
                blockers.append(str(exc))
        for name, digest in project.get("source_hashes", {}).items():
            try:
                if file_hash(local_path(root, name)) != digest:
                    blockers.append(f"Project validation stale after input change: {name}")
            except (OSError, ContractError) as exc:
                blockers.append(str(exc))
        target = Path(str(pptx.get("file", ""))).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            blockers.append("Inspected PPTX is missing or outside this workspace")
        elif not charts.get("pptx_sha256") or charts.get("pptx_sha256") != file_hash(target) or pptx.get("pptx_sha256") != file_hash(target):
            blockers.append("PPTX changed or chart/PPTX validation refers to a different artifact")

    for field in REQUIRED_MANUAL_CHECKS:
        value = manual.get(field) if isinstance(manual, dict) else None
        if not isinstance(value, bool):
            blockers.append(f"Manual review field must be boolean: {field}")
        elif value is not True:
            blockers.append(f"Manual review incomplete: {field}")

    accepted = (
        manual.get("warnings_accepted", [])
        if isinstance(manual, dict)
        else []
    )
    if not isinstance(accepted, list):
        blockers.append("manual-review.json warnings_accepted must be a list")
        accepted = []

    source_warnings = []
    if isinstance(project, dict):
        source_warnings.extend(project.get("warnings", []))
    if isinstance(pptx, dict):
        source_warnings.extend(pptx.get("warnings", []))
    for warning in source_warnings:
        if warning not in accepted:
            warnings.append(f"Unaccepted warning: {warning}")

    passed = not blockers and not warnings
    result = {
        "passed": passed,
        "verdict": "PASS — delivery authorized" if passed else "FAIL — delivery blocked",
        "blockers": blockers,
        "warnings": warnings,
        "manual_checks": {
            field: manual.get(field) if isinstance(manual, dict) else None
            for field in REQUIRED_MANUAL_CHECKS
        },
        "inputs": {
            "project_validation": "qa/project-validation.json",
            "pptx_inspection": "qa/pptx-inspection.json",
            "manual_review": "qa/manual-review.json",
        },
    }

    output = (
        Path(args.output).expanduser().resolve()
        if args.output
        else qa_dir / "final-gate.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
