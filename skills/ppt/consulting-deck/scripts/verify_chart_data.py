#!/usr/bin/env python3
"""Reconcile native chart caches and embedded workbook cells with source contracts.

Read-only for inputs. Explicit --output writes only the requested JSON report.
Supports ordinary native bar/line charts with A1 workbook ranges. Unsupported
references fail closed; file presence/object counts are never called data proof.
"""
from __future__ import annotations

import argparse
import io
import json
import math
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from exhibit_contracts import ContractError, file_hash, local_path, read_json

NS = {"p":"http://schemas.openxmlformats.org/presentationml/2006/main",
      "a":"http://schemas.openxmlformats.org/drawingml/2006/main",
      "c":"http://schemas.openxmlformats.org/drawingml/2006/chart",
      "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "s":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def xml(package, name):
    return ET.fromstring(package.read(name))


def relationships(package, owner):
    folder, name = posixpath.split(owner)
    rel_path = posixpath.join(folder,"_rels",name+".rels")
    if rel_path not in package.namelist():
        return {}
    result = {}
    for rel in xml(package,rel_path):
        if rel.get("TargetMode") == "External":
            result[rel.get("Id")] = None
        else:
            target = rel.get("Target", "")
            resolved = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(folder,target))
            if resolved.startswith("../"):
                raise ContractError("Package relationship escapes archive")
            result[rel.get("Id")] = resolved
    return result


def slide_parts(package):
    owner = "ppt/presentation.xml"
    rels = relationships(package,owner)
    return [rels[n.get(f"{{{NS['r']}}}id")] for n in xml(package,owner).findall("p:sldIdLst/p:sldId",NS)]


def cached_values(node):
    if node is None:
        raise ContractError("Missing chart data node")
    pts = node.findall(".//c:pt",NS)
    indexed = {}
    for pt in pts:
        index = int(pt.get("idx", "-1"))
        if index in indexed or index < 0:
            raise ContractError("Duplicate/invalid cache point index")
        indexed[index] = pt.findtext("c:v",default="",namespaces=NS)
    if indexed and sorted(indexed) != list(range(len(indexed))):
        raise ContractError("Sparse chart cache cannot be verified")
    return [indexed[i] for i in sorted(indexed)]


def cell_value(cell, strings):
    if cell is None:
        raise ContractError("Referenced workbook cell is absent")
    kind = cell.get("t")
    value = cell.findtext("s:v",namespaces=NS)
    if kind == "s":
        return strings[int(value)]
    if kind == "inlineStr":
        return "".join(n.text or "" for n in cell.findall(".//s:t",NS))
    if value is None:
        raise ContractError("Referenced workbook cell has no cached value")
    if kind in {"str","e","b"}:
        return value
    return float(value)


def col_number(column):
    number = 0
    for ch in column:
        number = number*26 + ord(ch)-64
    return number


def col_name(number):
    name = ""
    while number:
        number, digit = divmod(number-1,26)
        name = chr(65+digit)+name
    return name


def workbook_values(workbook, formula):
    match = re.fullmatch(r"(?:'((?:[^']|'')+)'|([^'!\[\]]+))!\$?([A-Z]+)\$?(\d+)(?::\$?([A-Z]+)\$?(\d+))?",formula or "")
    if not match:
        raise ContractError(f"Unsupported workbook formula: {formula}")
    quoted, plain, c1, r1, c2, r2 = match.groups()
    sheet = quoted.replace("''", "'") if quoted else plain
    c2, r2 = c2 or c1, r2 or r1
    ca, cb, ra, rb = col_number(c1), col_number(c2), int(r1), int(r2)
    if ca > cb or ra > rb or (ca != cb and ra != rb) or (cb-ca+1)*(rb-ra+1)>10000:
        raise ContractError("Only bounded row/column A1 ranges are supported")
    with zipfile.ZipFile(io.BytesIO(workbook)) as package:
        wb = xml(package,"xl/workbook.xml")
        rels = relationships(package,"xl/workbook.xml")
        chosen = next((s for s in wb.findall("s:sheets/s:sheet",NS) if s.get("name")==sheet),None)
        if chosen is None:
            raise ContractError(f"Workbook sheet absent: {sheet}")
        part = rels.get(chosen.get(f"{{{NS['r']}}}id"))
        if not part:
            raise ContractError("External/missing worksheet relationship")
        strings = []
        if "xl/sharedStrings.xml" in package.namelist():
            strings = ["".join(t.text or "" for t in n.findall(".//s:t",NS)) for n in xml(package,"xl/sharedStrings.xml")]
        cells = {c.get("r"):c for c in xml(package,part).findall(".//s:sheetData/s:row/s:c",NS)}
        return [cell_value(cells.get(f"{col_name(c)}{r}"),strings) for r in range(ra,rb+1) for c in range(ca,cb+1)]


def equal(actual, expected, context, numeric=False):
    if len(actual) != len(expected):
        raise ContractError(f"{context}: count differs ({len(actual)} vs {len(expected)})")
    for i,(a,e) in enumerate(zip(actual,expected)):
        if numeric:
            try:
                a, e = float(a), float(e)
            except (ValueError,TypeError) as exc:
                raise ContractError(f"{context}[{i}]: non-numeric value") from exc
            if not (math.isfinite(a) and math.isfinite(e) and math.isclose(a,e,rel_tol=1e-9,abs_tol=1e-10)):
                raise ContractError(f"{context}[{i}]: {a} != source {e}")
        elif (format(a,'.15g') if isinstance(a,(int,float)) else str(a)) != str(e):
            raise ContractError(f"{context}[{i}]: {a!r} != source {e!r}")


def verify_chart(package, chart_part, contract):
    tree = xml(package,chart_part)
    if tree.find(".//c:barChart",NS) is None and tree.find(".//c:lineChart",NS) is None:
        raise ContractError("Unsupported chart family; not reported as reconciled")
    series = tree.findall(".//c:ser",NS)
    expected = contract["series"]
    if len(series) != len(expected):
        raise ContractError("Chart series count differs from source")
    embedded = tree.find("c:externalData",NS)
    wb_part = None
    if embedded is not None:
        wb_part = relationships(package,chart_part).get(embedded.get(f"{{{NS['r']}}}id"))
    if contract.get("require_workbook",True) and not wb_part:
        raise ContractError("Editable chart workbook absent or external")
    workbook = package.read(wb_part) if wb_part else None
    for i,(s,expected_series) in enumerate(zip(series,expected)):
        categories, values = s.find("c:cat",NS), s.find("c:val",NS)
        equal(cached_values(categories),contract["categories"],f"series {i} categories")
        equal(cached_values(values),expected_series["values"],f"series {i} values",numeric=True)
        tx = s.find("c:tx",NS)
        name = tx.findtext("c:v",namespaces=NS) if tx is not None else None
        if name is None:
            names = cached_values(tx)
            name = names[0] if len(names)==1 else None
        equal([name],[expected_series["name"]],f"series {i} name")
        if workbook:
            for label,node,expected_values,numeric in (("categories",categories,contract["categories"],False),
                ("values",values,expected_series["values"],True)):
                formula = node.findtext(".//c:f",namespaces=NS)
                if not formula:
                    raise ContractError(f"Workbook is present but {label} has no verified range")
                equal(workbook_values(workbook,formula),expected_values,f"series {i} workbook {label}",numeric)
            name_formula = tx.findtext(".//c:f",namespaces=NS) if tx is not None else None
            if name_formula:
                equal(workbook_values(workbook,name_formula),[expected_series["name"]],f"series {i} workbook name")
    formats = [node.get("formatCode") for node in tree.findall(".//c:numFmt",NS)]
    if contract.get("number_format") and contract["number_format"] not in formats:
        raise ContractError("Declared numeric display format absent from exported chart")
    return {"chart_id":contract["chart_id"],"part":chart_part,"status":"passed",
            "source_cache_reconciled":True,"workbook_reconciled":bool(workbook),"series_count":len(series)}


def verify(pptx: Path, contract: dict, workspace: Path) -> dict:
    blockers, details = [], []
    for name,digest in contract.get("source_hashes",{}).items():
        try:
            if file_hash(local_path(workspace,name)) != digest:
                blockers.append(f"Canonical input changed since compilation: {name}")
        except (OSError,ContractError) as exc:
            blockers.append(str(exc))
    if not contract.get("source_hashes"):
        blockers.append("No canonical input hashes; cannot establish source lineage")
    try:
        with zipfile.ZipFile(pptx) as package:
            slides = slide_parts(package)
            owners = {s["slide_number"]:s for s in contract.get("slides",[])}
            if len(owners) != len(contract.get("slides",[])) or set(owners) != set(range(1,len(slides)+1)):
                raise ContractError("Contract must cover every slide exactly once")
            for number,part in enumerate(slides,1):
                if not part:
                    raise ContractError("External slide relationship")
                rels = relationships(package,part)
                refs = xml(package,part).findall(".//c:chart",NS)
                specs = owners[number].get("charts",[])
                if len(refs) != len(specs):
                    blockers.append(f"Slide {number}: native chart count differs from contract")
                    continue
                orders = [s.get("chart_order") for s in specs]
                if sorted(orders) != list(range(1,len(refs)+1)):
                    raise ContractError("Chart order must uniquely cover all native charts")
                for spec in specs:
                    try:
                        chart_part = rels.get(refs[spec["chart_order"]-1].get(f"{{{NS['r']}}}id"))
                        if not chart_part:
                            raise ContractError("External/missing chart relationship")
                        details.append({"slide_number":number,**verify_chart(package,chart_part,spec)})
                    except (ContractError,KeyError,ValueError,ET.ParseError,zipfile.BadZipFile) as exc:
                        blockers.append(f"Slide {number} {spec.get('chart_id')}: {exc}")
    except (OSError,zipfile.BadZipFile,ET.ParseError,KeyError,ContractError,TypeError) as exc:
        blockers.append(str(exc))
    return {"status":"failed" if blockers else "passed","passed":not blockers,"pptx_sha256":file_hash(pptx) if pptx.is_file() else None,
            "source_hashes":contract.get("source_hashes",{}),"charts":details,"blockers":blockers,
            "limitations":["Source extraction accuracy and chart interpretation require human review.",
                           "Data reconciliation does not prove rendered fit or PowerPoint application compatibility."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx"); parser.add_argument("--contract",required=True)
    parser.add_argument("--workspace",required=True); parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = verify(Path(args.pptx).resolve(),read_json(Path(args.contract)),Path(args.workspace).resolve())
    except (ContractError,KeyError,TypeError,ValueError) as exc:
        result = {"status":"failed","passed":False,"blockers":[str(exc)]}
    encoded = json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if args.output:
        output = Path(args.output).resolve()
        source_paths = {local_path(Path(args.workspace).resolve(),name) for name in result.get("source_hashes",{})}
        if output in {Path(args.pptx).resolve(),Path(args.contract).resolve()} | source_paths:
            parser.error("Report cannot overwrite a PPTX or contract input")
        output.parent.mkdir(parents=True,exist_ok=True); output.write_text(encoded,encoding="utf-8")
    print(encoded)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
