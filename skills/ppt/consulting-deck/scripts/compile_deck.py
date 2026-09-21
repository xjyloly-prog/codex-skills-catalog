#!/usr/bin/env python3
"""Compile bound content and chart data into a disposable local native-exhibit plan."""
import argparse
import json
from pathlib import Path
from exhibit_contracts import ContractError, compile_workspace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.project_dir).resolve()
    try:
        plan = compile_workspace(root, Path(__file__).resolve().parents[1] / "assets/layouts/native-exhibits.json")
    except (ContractError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({"status": "failed", "blockers": [str(exc)]}, ensure_ascii=False))
        return 1
    output = Path(args.output).resolve()
    if output in {(root / name).resolve() for name in plan["source_hashes"]}:
        parser.error("Output cannot overwrite a canonical input")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status":"passed", "slides":len(plan["slides"]), "output":str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
