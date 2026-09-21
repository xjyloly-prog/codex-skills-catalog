"""Local, dependency-free data/content contracts for native exhibits.

No network, package installation, execution of user code, or writes here.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import unicodedata
from pathlib import Path


class ContractError(ValueError):
    pass


def local_path(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ContractError("Expected a nonempty workspace-relative path")
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ContractError(f"Path escapes workspace: {relative}")
    return candidate


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ContractError(f"Cannot read JSON {path.name}: {exc}") from exc


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def width_units(text: str) -> float:
    # Approximation only. Final font metrics/rendering still decide fit.
    return sum(1 if unicodedata.east_asian_width(c) in "WF" else .55 for c in text)


def finite(value, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{label}: expected finite number; missing values are not zero")
    return value


def load_dataset(root: Path, chart: dict) -> dict:
    source = local_path(root, chart.get("data_path"))
    if source.suffix.lower() == ".csv":
        # Explicit wide CSV mapping. Never guess columns or units.
        mapping = chart.get("csv_mapping", {})
        category = mapping.get("category")
        columns = mapping.get("series", [])
        if not category or not columns:
            raise ContractError("CSV needs csv_mapping.category and series [{id,name,column}]")
        try:
            with source.open(encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                headers = reader.fieldnames or []
                required = [category] + [s["column"] for s in columns]
                if any(k not in headers for k in required):
                    raise ContractError("CSV mapping refers to absent columns")
                rows = list(reader)
            data = {"categories": [r[category] for r in rows], "series": []}
            for s in columns:
                try:
                    values = [float(r[s["column"]]) for r in rows]
                except (ValueError, KeyError) as exc:
                    raise ContractError(f"CSV {s['column']}: blank/non-numeric value") from exc
                data["series"].append({"id": s["id"], "name": s["name"], "values": values})
            data.update({k: chart.get(k) for k in ("unit", "value_scale")})
        except OSError as exc:
            raise ContractError(f"Cannot read CSV: {exc}") from exc
    else:
        data = read_json(source)
    if not isinstance(data, dict):
        raise ContractError("Chart dataset must be an object")
    categories, series = data.get("categories"), data.get("series")
    if not isinstance(categories, list) or not categories or any(not isinstance(c, str) or not c.strip() for c in categories):
        raise ContractError("Categories must be nonempty strings")
    if len(set(categories)) != len(categories):
        raise ContractError("Duplicate categories; use unambiguous labels")
    if not isinstance(series, list) or not series:
        raise ContractError("Dataset needs nonempty series")
    identifiers, names = set(), set()
    for s in series:
        if not isinstance(s, dict) or not s.get("id") or not isinstance(s.get("name"), str) or not s["name"].strip():
            raise ContractError("Each series needs stable id and name")
        if s["id"] in identifiers or s["name"] in names:
            raise ContractError("Duplicate series ID or name")
        identifiers.add(s["id"]); names.add(s["name"])
        values = s.get("values")
        if not isinstance(values, list) or len(values) != len(categories):
            raise ContractError(f"{s['id']}: categories/value length mismatch")
        for i, value in enumerate(values):
            finite(value, f"{s['id']}[{i}]")
    unit, scale = data.get("unit"), data.get("value_scale", "raw")
    if not isinstance(unit, str) or not unit.strip():
        raise ContractError("Dataset must declare unit")
    if chart.get("unit") != unit:
        raise ContractError(f"Chart/dataset unit mismatch: {chart.get('unit')} vs {unit}")
    if scale not in {"raw", "fraction", "percent-points"}:
        raise ContractError("value_scale must be raw, fraction, or percent-points")
    if unit == "%" and scale not in {"fraction", "percent-points"}:
        raise ContractError("Percent data must explicitly declare fraction or percent-points")
    if unit != "%" and scale != "raw":
        raise ContractError("Only % data may use fraction/percent-points scale")
    divisor = 100 if scale == "percent-points" else 1
    data = {**data, "value_scale": scale,
            "series": [{**s, "values": list(s["values"])} for s in series]}
    # Do not reorder, round, truncate, normalize to 100%, or fill missing data.
    if chart.get("component_type") == "survey":
        if unit != "%":
            raise ContractError("Survey distribution requires %")
        tolerance = chart.get("sum_tolerance", 1.1)
        finite(tolerance, "sum_tolerance")
        if not 0 <= tolerance <= 2:
            raise ContractError("Survey sum_tolerance must be between 0 and 2 percentage points")
        for i in range(len(categories)):
            values = [s["values"][i] / divisor for s in series]
            if any(v < 0 or v > 1 for v in values):
                raise ContractError(f"Survey {categories[i]}: values outside 0–100%")
            total = sum(values)
            if abs(total - 1) * 100 > tolerance + 1e-8:
                raise ContractError(f"Survey {categories[i]} totals {total * 100:g}%, outside declared tolerance")
    if chart.get("component_type") in {"stacked", "survey"} and any(v < 0 for s in series for v in s["values"]):
        raise ContractError("Negative stacks require a dedicated diverging chart, not this component")
    return data


def resolve_copy(slide: dict, contents: dict) -> dict:
    bindings = slide.get("content_bindings", {})
    if not isinstance(bindings, dict):
        raise ContractError("content_bindings must be an object")
    resolved = {}
    for key in ("action_title", "subtitle", "implication"):
        content_id = bindings.get(key)
        if content_id:
            if key in slide:
                raise ContractError(f"{key}: bound content and duplicate literal are not allowed")
            item = contents.get(content_id)
            if not isinstance(item, dict) or not isinstance(item.get("text"), str) or not item["text"].strip():
                raise ContractError(f"Unknown/empty content binding: {content_id}")
            resolved[key] = item["text"]
        else:
            resolved[key] = slide.get(key, "")
            if not isinstance(resolved[key], str):
                raise ContractError(f"{key} must be text")
    if not resolved["action_title"].strip():
        raise ContractError("Missing action_title binding")
    return resolved


def fits_layout(layout: dict, panels: list[dict], variant: str) -> list[str]:
    failures = []
    if variant not in layout["variants"]:
        failures.append(f"variant {variant} unsupported")
    if not layout["panels"][0] <= len(panels) <= layout["panels"][1]:
        failures.append("panel count exceeds capacity")
    for i, panel in enumerate(panels):
        types = (layout.get("panel_types") or [layout.get("types", [])] * len(panels))
        if i >= len(types) or panel["component_type"] not in types[i]:
            failures.append(f"panel {i + 1}: incompatible component type")
        for key, count in (("categories", len(panel["data"]["categories"])), ("series", len(panel["data"]["series"]))):
            low, high = layout[key]
            if not low <= count <= high:
                failures.append(f"panel {i + 1}: {key} count {count} outside {low}–{high}")
    return failures


def compile_workspace(root: Path, manifest_path: Path) -> dict:
    manifest = read_json(manifest_path)
    layouts = {l["id"]: l for l in manifest["layouts"]}
    slides, charts = read_json(root / "slides.json"), read_json(root / "charts.json")
    content = read_json(root / "content.json")
    evidence = read_json(root / "evidence.json") if (root / "evidence.json").is_file() else []
    evidence_ids = {e.get("evidence_id") for e in evidence if isinstance(e, dict)}
    if not isinstance(slides, list) or not isinstance(charts, list) or not isinstance(content, dict):
        raise ContractError("slides/charts must be arrays and content must be an object")
    contents, chart_map, slide_ids = {}, {}, set()
    for item in content.get("items", []):
        cid = item.get("content_id")
        if not cid or cid in contents:
            raise ContractError("Missing/duplicate content_id")
        contents[cid] = item
        if any(eid not in evidence_ids for eid in item.get("evidence_ids", [])):
            raise ContractError(f"{cid}: unknown linked evidence")
    for chart in charts:
        cid = chart.get("chart_id")
        if not cid or cid in chart_map:
            raise ContractError("Missing/duplicate chart_id")
        chart_map[cid] = chart
    source_files = {"slides.json", "charts.json", "content.json"}
    for name in ("brief.json", "evidence.json", "storyline.json", "design-system.json"):
        if (root / name).is_file():
            source_files.add(name)
    resolved_slides = []
    for slide in slides:
        sid, lid = slide.get("slide_id"), slide.get("layout_id")
        if not sid or sid in slide_ids:
            raise ContractError("Missing/duplicate slide_id")
        slide_ids.add(sid)
        if lid not in layouts:
            raise ContractError(f"{sid}: {lid} not in executable exhibit subset; use host-native authoring for other layouts")
        copy = resolve_copy(slide, contents)
        panels = []
        for cid in slide.get("chart_ids", []):
            if cid not in chart_map:
                raise ContractError(f"{sid}: unknown chart {cid}")
            chart = chart_map[cid]
            if not chart.get("source_locator"):
                raise ContractError(f"{cid}: source locator is required")
            if chart.get("slide_id") != sid:
                raise ContractError(f"{cid}: chart belongs to another slide")
            data = load_dataset(root, chart)
            source_files.add(chart["data_path"])
            panels.append({"chart_id": cid, "component_type": chart.get("component_type"), "data": data,
                           "label": chart.get("display_title", ""), "source": chart.get("source_locator", ""),
                           "axis_min": chart.get("axis_min"), "axis_max": chart.get("axis_max"),
                           "axis_major_unit": chart.get("axis_major_unit"),
                           "focus_series": chart.get("focus_series"), "focus_categories": chart.get("focus_categories", []),
                           "decimals": chart.get("decimals", 0)})
        variant = slide.get("selected_variant", "wide")
        failures = fits_layout(layouts[lid], panels, variant)
        limits = manifest["copy_limits"]
        for key, limit_key in (("action_title", "title_width_units"), ("subtitle", "subtitle_width_units"),
                               ("implication", "rail_implication_width_units" if variant == "rail" else "implication_width_units")):
            if width_units(copy[key]) > limits[limit_key]:
                failures.append(f"{key} exceeds estimated capacity; split/rewrite/change layout, do not shrink")
        for panel in panels:
            if width_units(panel["label"]) > limits["panel_title_width_units"]:
                failures.append("panel title exceeds estimated capacity")
            if any(width_units(c) > limits["category_width_units"] for c in panel["data"]["categories"]):
                failures.append("category label exceeds estimated capacity")
        if failures:
            raise ContractError(f"{sid}: " + "; ".join(failures))
        if layouts[lid].get("shared_scale"):
            if len({(p["data"]["unit"], p["data"]["value_scale"]) for p in panels}) != 1:
                raise ContractError(f"{sid}: shared scale requires identical units and value scales")
            values = [v / (100 if p["data"]["value_scale"] == "percent-points" else 1)
                      for p in panels for s in p["data"]["series"] for v in s["values"]]
            minimum, maximum = min(0, min(values)), max(0, max(values))
            if maximum == minimum:
                maximum = minimum + 1
            bounded_percent = panels[0]["data"]["unit"] == "%" and minimum == 0 and maximum <= 1
            panels = [{**p, "axis_min": minimum,
                       "axis_max": 1 if bounded_percent else maximum * 1.15 if maximum > 0 else maximum,
                       "axis_major_unit": .2 if bounded_percent else None} for p in panels]
        resolved_slides.append({"slide_id": sid, "layout_id": lid, "variant": variant,
                                "display_order": slide.get("display_order", len(resolved_slides) + 1), **copy, "panels": panels})
    orders = [s["display_order"] for s in resolved_slides]
    if any(not isinstance(x, int) or isinstance(x, bool) or x < 1 for x in orders) or len(set(orders)) != len(orders):
        raise ContractError("display_order must contain distinct positive integers")
    assigned = [p["chart_id"] for s in resolved_slides for p in s["panels"]]
    if len(assigned) != len(set(assigned)) or set(chart_map) != set(assigned):
        raise ContractError("All component chart specs must be referenced exactly once")
    return {"schema_version": 1, "canvas": manifest["canvas"],
            "slides": sorted(resolved_slides, key=lambda s: s["display_order"]),
            "source_hashes": {name: file_hash(local_path(root, name)) for name in sorted(source_files)}}
