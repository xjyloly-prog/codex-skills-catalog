#!/usr/bin/env python3
"""Run portable structural checks on a PowerPoint OOXML package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def numeric_key(name: str) -> int:
    match = re.search(r"(\d+)\.xml$", name)
    return int(match.group(1)) if match else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output", help="Optional path for the JSON result")
    args = parser.parse_args()

    path = Path(args.pptx).expanduser().resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    slide_details: list[dict[str, object]] = []
    aspect_ratio = "unknown"

    if not path.is_file():
        blockers.append(f"File does not exist: {path}")
    elif not zipfile.is_zipfile(path):
        blockers.append("File is not a valid ZIP-based PPTX package")
    else:
        try:
            with zipfile.ZipFile(path) as package:
                names = set(package.namelist())
                for required in ("[Content_Types].xml", "ppt/presentation.xml"):
                    if required not in names:
                        blockers.append(f"Missing package part: {required}")

                if "ppt/presentation.xml" in names:
                    presentation = ET.fromstring(package.read("ppt/presentation.xml"))
                    size = presentation.find("p:sldSz", NS)
                    if size is not None:
                        cx = int(size.attrib.get("cx", "0"))
                        cy = int(size.attrib.get("cy", "0"))
                        if cy:
                            ratio = cx / cy
                            if abs(ratio - 16 / 9) < 0.03:
                                aspect_ratio = "16:9"
                            elif abs(ratio - 4 / 3) < 0.03:
                                aspect_ratio = "4:3"
                            else:
                                aspect_ratio = f"{ratio:.3f}:1"

                slide_names = sorted(
                    (
                        name
                        for name in names
                        if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
                    ),
                    key=numeric_key,
                )
                if not slide_names:
                    blockers.append("No slide XML parts found")

                image_only_count = 0
                for slide_name in slide_names:
                    root = ET.fromstring(package.read(slide_name))
                    text = "".join(node.text or "" for node in root.findall(".//a:t", NS))
                    shape_count = len(root.findall(".//p:sp", NS))
                    picture_count = len(root.findall(".//p:pic", NS))
                    frame_count = len(root.findall(".//p:graphicFrame", NS))
                    table_count = len(root.findall(".//a:tbl", NS))
                    image_only = picture_count > 0 and len(text.strip()) < 5 and shape_count <= 1
                    if image_only:
                        image_only_count += 1
                    slide_details.append(
                        {
                            "slide": numeric_key(slide_name),
                            "text_characters": len(text.strip()),
                            "shapes": shape_count,
                            "pictures": picture_count,
                            "graphic_frames": frame_count,
                            "tables": table_count,
                            "possible_image_only": image_only,
                        }
                    )

                if slide_names and image_only_count == len(slide_names):
                    blockers.append("Every slide appears to be flattened as an image")
                elif image_only_count:
                    warnings.append(
                        f"{image_only_count} slide(s) may be image-only; inspect covers "
                        "and visual slides manually"
                    )

                notes_count = len(
                    [
                        name
                        for name in names
                        if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", name)
                    ]
                )
                chart_count = len(
                    [
                        name
                        for name in names
                        if re.fullmatch(
                            r"ppt/(?:charts|slides/charts)/chart\d+\.xml",
                            name,
                        )
                    ]
                )
                if slide_names and notes_count == 0:
                    warnings.append("No speaker-note parts found")
        except (zipfile.BadZipFile, ET.ParseError, KeyError) as exc:
            blockers.append(f"Could not inspect PPTX package: {exc}")
            notes_count = 0
            chart_count = 0
            slide_names = []

    result = {
        "file": str(path),
        "status": "failed" if blockers else "passed_with_warnings" if warnings else "passed",
        "aspect_ratio": aspect_ratio,
        "slide_count": len(slide_details),
        "notes_count": locals().get("notes_count", 0),
        "native_chart_count": locals().get("chart_count", 0),
        "native_table_count": sum(
            int(slide.get("tables", 0)) for slide in slide_details
        ),
        "pptx_sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        "blockers": blockers,
        "warnings": warnings,
        "slides": slide_details,
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
        print(
            f"Slides: {result['slide_count']}; notes: {result['notes_count']}; "
            f"native charts: {result['native_chart_count']}; "
            f"native tables: {result['native_table_count']}; "
            f"aspect ratio: {aspect_ratio}"
        )
        for message in blockers:
            print(f"BLOCKER: {message}")
        for message in warnings:
            print(f"WARNING: {message}")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
