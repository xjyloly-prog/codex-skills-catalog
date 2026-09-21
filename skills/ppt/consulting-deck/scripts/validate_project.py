#!/usr/bin/env python3
"""Validate a consulting-deck project before PPTX production."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from exhibit_contracts import ContractError, compile_workspace, file_hash, read_json, resolve_copy


REQUIRED_FILES = (
    "brief.json",
    "evidence.json",
    "charts.json",
    "storyline.json",
    "design-system.json",
    "slides.json",
)
VALID_ROLES = {
    "orient",
    "assert",
    "prove",
    "compare",
    "explain",
    "decide",
    "mobilize",
    "reference",
}
VALID_LAYOUTS = {f"C{i:02d}" for i in range(1, 46)}
VALID_DECK_MODES = {
    "research-analytical",
    "executive-story",
    "editorial-keynote",
}
VALID_ANALYSIS_ROUTES = {"source-synthesis", "problem-solving"}
VALID_PRODUCTION_RUNTIMES = {
    "auto",
    "host-native",
    "ppt-master-adapter",
    "pptxgenjs",
}
VALID_HYPOTHESIS_STATES = {
    "pending",
    "supported",
    "rejected",
    "mixed",
    "untestable",
}
VALID_GENERATION_PHASES = {
    "independent",
    "dependent",
    "synthesis",
    "appendix",
}
VALID_EXHIBIT_TYPES = {
    "none",
    "chart",
    "table",
    "chart-table",
    "source-figure",
}
VALID_CHART_FAMILIES = {
    "deviation",
    "correlation",
    "ranking",
    "distribution",
    "magnitude",
    "time",
    "part-to-whole",
    "flow",
    "spatial",
    "matrix",
}
VALID_CHART_RENDERERS = {
    "native-pptx",
    "native-shapes",
    "vizro-preview",
    "source-image",
    "svg-fallback",
}
VALID_CHART_EDITABILITY = {
    "native-chart",
    "native-shapes",
    "image",
}
VALID_RECONCILIATION_STATES = {"pending", "passed", "failed"}
WEAK_TITLES = {
    "overview",
    "background",
    "analysis",
    "recommendations",
    "next steps",
    "概览",
    "背景",
    "分析",
    "建议",
    "下一步",
    "市场分析",
    "行业趋势",
}


def load_json(path: Path, blockers: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        blockers.append(f"Missing required file: {path.name}")
    except json.JSONDecodeError as exc:
        blockers.append(f"Invalid JSON in {path.name}: {exc}")
    return None


def is_zh_heavy(value: str) -> bool:
    return len(re.findall(r"[\u4e00-\u9fff]", value)) >= 4


def dependency_order(
    slide_ids: list[str],
    dependency_map: dict[str, list[str]],
) -> tuple[list[str], list[str]]:
    """Return a stable dependency-safe order and any nodes involved in a cycle."""
    index = {slide_id: position for position, slide_id in enumerate(slide_ids)}
    indegree = {slide_id: 0 for slide_id in slide_ids}
    dependents = {slide_id: [] for slide_id in slide_ids}

    for slide_id, requirements in dependency_map.items():
        for requirement in requirements:
            if slide_id in indegree and requirement in indegree:
                indegree[slide_id] += 1
                dependents[requirement].append(slide_id)

    ready = sorted(
        (slide_id for slide_id, count in indegree.items() if count == 0),
        key=index.get,
    )
    order: list[str] = []
    while ready:
        slide_id = ready.pop(0)
        order.append(slide_id)
        for dependent in sorted(dependents[slide_id], key=index.get):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                ready.append(dependent)
                ready.sort(key=index.get)

    cycle_nodes = [slide_id for slide_id in slide_ids if indegree[slide_id] > 0]
    return order, cycle_nodes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output", help="Optional path for the JSON result")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    advisories: list[str] = []

    if not root.is_dir():
        blockers.append(f"Project directory does not exist: {root}")

    docs = {
        name: load_json(root / name, blockers) if root.is_dir() else None
        for name in REQUIRED_FILES
    }
    brief = docs["brief.json"] if isinstance(docs["brief.json"], dict) else {}
    evidence = docs["evidence.json"] if isinstance(docs["evidence.json"], list) else []
    charts = docs["charts.json"] if isinstance(docs["charts.json"], list) else []
    storyline = (
        docs["storyline.json"] if isinstance(docs["storyline.json"], dict) else {}
    )
    slides = docs["slides.json"] if isinstance(docs["slides.json"], list) else []
    content_items = {}
    if (root / "content.json").is_file():
        try:
            content_doc = read_json(root / "content.json")
            for item in content_doc.get("items", []):
                cid = item.get("content_id")
                if not cid or cid in content_items:
                    blockers.append("content.json has missing/duplicate content_id")
                content_items[cid] = item
        except (ContractError, TypeError, AttributeError) as exc:
            blockers.append(str(exc))
    hypotheses_path = root / "hypotheses.json"
    if hypotheses_path.is_file():
        hypotheses_doc = load_json(hypotheses_path, blockers)
        hypotheses = hypotheses_doc if isinstance(hypotheses_doc, list) else []
    else:
        hypotheses = []
        advisories.append(
            "No hypotheses.json found; create one for topic-driven problem solving"
        )

    for field in (
        "project_id",
        "title",
        "audience",
        "decision",
        "deck_mode",
        "density",
        "language",
    ):
        if not str(brief.get(field, "")).strip():
            blockers.append(f"brief.json missing value: {field}")
    if brief.get("deck_mode") not in VALID_DECK_MODES:
        blockers.append(
            "brief.json deck_mode must be research-analytical, executive-story, "
            "or editorial-keynote"
        )
    if brief.get("density") not in {"speaker-led", "reading-first"}:
        blockers.append("brief.json density must be speaker-led or reading-first")
    production_runtime = brief.get("production_runtime", "auto")
    if "production_runtime" not in brief:
        advisories.append(
            "brief.json has no production_runtime; treating it as auto"
        )
    elif production_runtime not in VALID_PRODUCTION_RUNTIMES:
        blockers.append(
            "brief.json production_runtime must be auto, host-native, "
            "ppt-master-adapter, or pptxgenjs"
        )
    analysis_route = brief.get("analysis_route", "source-synthesis")
    if "analysis_route" not in brief:
        advisories.append(
            "brief.json has no analysis_route; treating it as source-synthesis"
        )
    elif analysis_route not in VALID_ANALYSIS_ROUTES:
        blockers.append(
            "brief.json analysis_route must be source-synthesis or problem-solving"
        )
    if analysis_route == "problem-solving":
        if not str(brief.get("problem_statement", "")).strip():
            blockers.append(
                "brief.json problem_statement is required for problem-solving"
            )
        if not hypotheses:
            blockers.append(
                "problem-solving route requires at least one hypothesis record"
            )
    if not str(storyline.get("governing_thought", "")).strip():
        blockers.append("storyline.json missing governing_thought")
    if not str(storyline.get("audience_question", "")).strip():
        blockers.append("storyline.json missing audience_question")

    evidence_ids: list[str] = []
    for index, item in enumerate(evidence):
        if not isinstance(item, dict):
            blockers.append(f"evidence.json item {index + 1} is not an object")
            continue
        evidence_id = str(item.get("evidence_id", "")).strip()
        if not evidence_id:
            blockers.append(f"evidence.json item {index + 1} missing evidence_id")
        else:
            evidence_ids.append(evidence_id)
        if item.get("type") not in {
            "fact",
            "data",
            "quotation",
            "interpretation",
            "hypothesis",
        }:
            blockers.append(f"{evidence_id or index + 1}: invalid evidence type")
        if item.get("type") != "hypothesis":
            if not str(item.get("source", "")).strip():
                blockers.append(f"{evidence_id}: missing source")
            if not str(item.get("locator", "")).strip():
                warnings.append(f"{evidence_id}: missing precise source locator")
    duplicates = [key for key, count in Counter(evidence_ids).items() if count > 1]
    if duplicates:
        blockers.append(f"Duplicate evidence IDs: {', '.join(sorted(duplicates))}")
    evidence_set = set(evidence_ids)

    hypothesis_ids: list[str] = []
    hypothesis_slide_refs: dict[str, list[str]] = {}
    for index, item in enumerate(hypotheses):
        if not isinstance(item, dict):
            blockers.append(f"hypotheses.json item {index + 1} is not an object")
            continue
        hypothesis_id = str(item.get("hypothesis_id", "")).strip()
        if not hypothesis_id:
            blockers.append(
                f"hypotheses.json item {index + 1} missing hypothesis_id"
            )
        else:
            hypothesis_ids.append(hypothesis_id)
        for field in ("issue", "statement", "validation_plan"):
            if not str(item.get(field, "")).strip():
                blockers.append(
                    f"{hypothesis_id or index + 1}: missing hypothesis field {field}"
                )
        if item.get("status") not in VALID_HYPOTHESIS_STATES:
            blockers.append(
                f"{hypothesis_id or index + 1}: invalid hypothesis status"
            )
        for field in ("confirming_evidence_ids", "contrary_evidence_ids"):
            references = item.get(field, [])
            if not isinstance(references, list):
                blockers.append(
                    f"{hypothesis_id or index + 1}: {field} must be a list"
                )
                continue
            for evidence_id in references:
                if evidence_id not in evidence_set:
                    blockers.append(
                        f"{hypothesis_id or index + 1}: unknown evidence_id "
                        f"{evidence_id} in {field}"
                    )
        slide_refs = item.get("slide_ids", [])
        if not isinstance(slide_refs, list):
            blockers.append(
                f"{hypothesis_id or index + 1}: slide_ids must be a list"
            )
            slide_refs = []
        hypothesis_slide_refs[hypothesis_id] = slide_refs
        if (
            item.get("status") in {"supported", "rejected", "mixed"}
            and not item.get("confirming_evidence_ids")
            and not item.get("contrary_evidence_ids")
        ):
            warnings.append(
                f"{hypothesis_id}: resolved hypothesis has no linked evidence"
            )
    duplicate_hypotheses = [
        key for key, count in Counter(hypothesis_ids).items() if count > 1
    ]
    if duplicate_hypotheses:
        blockers.append(
            f"Duplicate hypothesis IDs: {', '.join(sorted(duplicate_hypotheses))}"
        )

    chart_ids: list[str] = []
    chart_slide_refs: dict[str, str] = {}
    for index, item in enumerate(charts):
        if not isinstance(item, dict):
            blockers.append(f"charts.json item {index + 1} is not an object")
            continue
        chart_id = str(item.get("chart_id", "")).strip()
        slide_id = str(item.get("slide_id", "")).strip()
        if not chart_id:
            blockers.append(f"charts.json item {index + 1} missing chart_id")
        else:
            chart_ids.append(chart_id)
            chart_slide_refs[chart_id] = slide_id
        for field in (
            "slide_id",
            "question",
            "conclusion",
            "subtype",
            "data_path",
            "source_locator",
        ):
            if not str(item.get(field, "")).strip():
                blockers.append(f"{chart_id or index + 1}: missing chart field {field}")
        if item.get("family") not in VALID_CHART_FAMILIES:
            blockers.append(f"{chart_id or index + 1}: invalid chart family")
        if item.get("renderer") not in VALID_CHART_RENDERERS:
            blockers.append(f"{chart_id or index + 1}: invalid chart renderer")
        if item.get("editability") not in VALID_CHART_EDITABILITY:
            blockers.append(f"{chart_id or index + 1}: invalid editability value")
        reconciliation = item.get("reconciliation")
        if reconciliation not in VALID_RECONCILIATION_STATES:
            blockers.append(
                f"{chart_id or index + 1}: reconciliation must be pending, passed, "
                "or failed"
            )
        elif reconciliation == "failed":
            blockers.append(f"{chart_id or index + 1}: chart reconciliation failed")
        elif reconciliation == "pending":
            warnings.append(f"{chart_id or index + 1}: chart reconciliation pending")
        if item.get("renderer") == "vizro-preview":
            warnings.append(
                f"{chart_id or index + 1}: Vizro preview must be converted to an "
                "editable final exhibit"
            )
        if item.get("editability") == "image":
            warnings.append(
                f"{chart_id or index + 1}: image-based chart requires explicit "
                "fidelity justification"
            )
    duplicate_charts = [key for key, count in Counter(chart_ids).items() if count > 1]
    if duplicate_charts:
        blockers.append(f"Duplicate chart IDs: {', '.join(sorted(duplicate_charts))}")
    chart_set = set(chart_ids)

    slide_ids: list[str] = []
    layout_ids: list[str] = []
    titles: list[str] = []
    evidence_led_count = 0
    native_chart_table_count = 0
    dependency_map: dict[str, list[str]] = {}
    display_orders: list[int] = []
    missing_dependency_metadata = False
    for index, item in enumerate(slides):
        if not isinstance(item, dict):
            blockers.append(f"slides.json item {index + 1} is not an object")
            continue
        slide_id = str(item.get("slide_id", "")).strip()
        try:
            title = resolve_copy(item, content_items)["action_title"].strip()
        except ContractError as exc:
            blockers.append(f"{slide_id or index + 1}: {exc}")
            title = ""
        layout_id = str(item.get("layout_id", "")).strip()
        role = str(item.get("page_role", "")).strip()
        exhibit_type = str(item.get("exhibit_type", "")).strip()
        generation_phase = item.get("generation_phase")
        requires_slide_ids = item.get("requires_slide_ids", [])
        display_order = item.get("display_order")
        if not slide_id:
            blockers.append(f"Slide {index + 1}: missing slide_id")
        else:
            slide_ids.append(slide_id)
        if not title:
            blockers.append(f"{slide_id or index + 1}: missing action_title")
        else:
            titles.append(title)
            if title.strip().lower() in WEAK_TITLES:
                warnings.append(f"{slide_id}: topic title is not answer-first: {title}")
            if is_zh_heavy(title) and len(re.findall(r"[\u4e00-\u9fff]", title)) > 36:
                warnings.append(f"{slide_id}: Chinese action title may be too long")
            if not is_zh_heavy(title) and len(title.split()) > 18:
                warnings.append(f"{slide_id}: English action title may be too long")
        if layout_id not in VALID_LAYOUTS:
            blockers.append(f"{slide_id or index + 1}: invalid layout_id {layout_id!r}")
        else:
            layout_ids.append(layout_id)
        if role not in VALID_ROLES:
            blockers.append(f"{slide_id or index + 1}: invalid page_role {role!r}")
        if generation_phase is None:
            missing_dependency_metadata = True
        elif generation_phase not in VALID_GENERATION_PHASES:
            blockers.append(
                f"{slide_id or index + 1}: invalid generation_phase "
                f"{generation_phase!r}"
            )
        if not isinstance(requires_slide_ids, list):
            blockers.append(
                f"{slide_id or index + 1}: requires_slide_ids must be a list"
            )
            requires_slide_ids = []
        if slide_id:
            dependency_map[slide_id] = list(dict.fromkeys(requires_slide_ids))
        if display_order is None:
            missing_dependency_metadata = True
        elif not isinstance(display_order, int) or display_order < 1:
            blockers.append(
                f"{slide_id or index + 1}: display_order must be a positive integer"
            )
        else:
            display_orders.append(display_order)
        if exhibit_type not in VALID_EXHIBIT_TYPES:
            blockers.append(
                f"{slide_id or index + 1}: invalid exhibit_type {exhibit_type!r}"
            )
        elif exhibit_type != "none":
            evidence_led_count += 1
        if item.get("native_chart_expected") is True:
            native_chart_table_count += 1
            if not str(item.get("chart_data_path", "")).strip():
                warnings.append(
                    f"{slide_id or index + 1}: native chart/table expected but "
                    "chart_data_path is empty"
                )
            if not item.get("chart_ids"):
                blockers.append(
                    f"{slide_id or index + 1}: native chart/table expected but "
                    "chart_ids is empty"
                )
        linked_chart_ids = item.get("chart_ids", [])
        if not isinstance(linked_chart_ids, list):
            blockers.append(f"{slide_id or index + 1}: chart_ids must be a list")
            linked_chart_ids = []
        for chart_id in linked_chart_ids:
            if chart_id not in chart_set:
                blockers.append(
                    f"{slide_id or index + 1}: unknown chart_id {chart_id}"
                )
            elif chart_slide_refs.get(chart_id) != slide_id:
                blockers.append(
                    f"{slide_id or index + 1}: chart_id {chart_id} points to "
                    f"slide {chart_slide_refs.get(chart_id)!r}"
                )
        for evidence_id in item.get("evidence_ids", []):
            if evidence_id not in evidence_set:
                blockers.append(
                    f"{slide_id or index + 1}: unknown evidence_id {evidence_id}"
                )

    duplicate_slides = [key for key, count in Counter(slide_ids).items() if count > 1]
    if duplicate_slides:
        blockers.append(f"Duplicate slide IDs: {', '.join(sorted(duplicate_slides))}")
    duplicate_titles = [key for key, count in Counter(titles).items() if count > 1]
    if duplicate_titles:
        warnings.append(f"Repeated action titles: {', '.join(duplicate_titles)}")
    slide_set = set(slide_ids)
    if missing_dependency_metadata and slides:
        advisories.append(
            "Some slides lack generation_phase or display_order dependency metadata"
        )
    duplicate_display_orders = [
        str(key) for key, count in Counter(display_orders).items() if count > 1
    ]
    if duplicate_display_orders:
        blockers.append(
            "Duplicate display_order values: "
            + ", ".join(sorted(duplicate_display_orders, key=int))
        )
    for slide_id, requirements in dependency_map.items():
        for requirement in requirements:
            if requirement == slide_id:
                blockers.append(f"{slide_id}: cannot depend on itself")
            elif requirement not in slide_set:
                blockers.append(
                    f"{slide_id}: unknown required slide_id {requirement}"
                )
    recommended_generation_order, cycle_nodes = dependency_order(
        slide_ids,
        dependency_map,
    )
    if cycle_nodes:
        blockers.append(
            "Slide dependency cycle detected: " + ", ".join(cycle_nodes)
        )
    for chart_id, slide_id in chart_slide_refs.items():
        if slide_id not in slide_set:
            blockers.append(f"{chart_id}: unknown slide_id {slide_id}")
    for hypothesis_id, referenced_slides in hypothesis_slide_refs.items():
        for slide_id in referenced_slides:
            if slide_id not in slide_set:
                blockers.append(
                    f"{hypothesis_id}: unknown slide_id {slide_id}"
                )

    slide_count = len(slides)
    distinct_layouts = len(set(layout_ids))
    required_variety = 7 if slide_count >= 10 else 5 if slide_count >= 7 else 0
    if required_variety and distinct_layouts < required_variety:
        warnings.append(
            f"Layout variety is low: {distinct_layouts} distinct layouts; "
            f"target at least {required_variety}"
        )
    for index in range(len(layout_ids) - 2):
        if len(set(layout_ids[index : index + 3])) == 1:
            warnings.append(
                f"Three consecutive slides reuse {layout_ids[index]} at positions "
                f"{index + 1}-{index + 3}"
            )

    if brief.get("deck_mode") == "research-analytical":
        if 7 <= slide_count <= 9:
            evidence_target, native_target = 4, 3
        elif 10 <= slide_count <= 12:
            evidence_target, native_target = 6, 5
        elif 13 <= slide_count <= 15:
            evidence_target, native_target = 8, 7
        else:
            evidence_target = max(1, round(slide_count * 0.6))
            native_target = max(1, round(slide_count * 0.45))
        if evidence_led_count < evidence_target:
            blockers.append(
                "Research Analytical mode requires at least "
                f"{evidence_target} evidence-led pages; found {evidence_led_count}"
            )
        if native_chart_table_count < native_target:
            blockers.append(
                "Research Analytical mode requires at least "
                f"{native_target} native chart/table pages; "
                f"found {native_chart_table_count}"
            )

    unreferenced = evidence_set - {
        evidence_id
        for slide in slides
        if isinstance(slide, dict)
        for evidence_id in slide.get("evidence_ids", [])
    }
    if unreferenced:
        advisories.append(
            f"Unused evidence records: {', '.join(sorted(unreferenced))}"
        )

    if brief.get("native_component_contract") == 1:
        try:
            compile_workspace(root, Path(__file__).resolve().parents[1] / "assets/layouts/native-exhibits.json")
        except (ContractError, KeyError, TypeError, AttributeError) as exc:
            blockers.append(f"Native exhibit contract: {exc}")

    result = {
        "project": str(root),
        "slide_count": slide_count,
        "evidence_count": len(evidence),
        "hypothesis_count": len(hypotheses),
        "chart_count": len(charts),
        "distinct_layouts": distinct_layouts,
        "evidence_led_pages": evidence_led_count,
        "native_chart_table_pages_planned": native_chart_table_count,
        "recommended_generation_order": recommended_generation_order,
        "blockers": blockers,
        "warnings": warnings,
        "advisories": advisories,
        "status": "failed" if blockers else "passed_with_warnings" if warnings else "passed",
        "source_hashes": {p.name: file_hash(p) for p in [root / n for n in REQUIRED_FILES] + [root / "content.json"] if p.is_file()},
    }
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {result['status']}")
        for label in ("blockers", "warnings", "advisories"):
            for message in result[label]:
                print(f"{label[:-1].upper()}: {message}")
        print(
            f"Slides: {slide_count}; hypotheses: {len(hypotheses)}; "
            f"evidence: {len(evidence)}; "
            f"charts: {len(charts)}; "
            f"distinct layouts: {distinct_layouts}; "
            f"evidence-led pages: {evidence_led_count}; "
            f"planned native chart/table pages: {native_chart_table_count}"
        )
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
