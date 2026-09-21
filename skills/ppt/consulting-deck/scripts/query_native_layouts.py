#!/usr/bin/env python3
"""Find capacity-compatible, structurally distinct native-exhibit candidates."""
import argparse
import hashlib
import json
from pathlib import Path
from exhibit_contracts import ContractError, fits_layout, load_dataset, read_json, resolve_copy, width_units


def query(root, slide_id, seed="consulting-deck", limit=3):
    manifest=read_json(Path(__file__).resolve().parents[1]/"assets/layouts/native-exhibits.json")
    slides=read_json(root/"slides.json")
    slide=next((s for s in slides if s.get("slide_id")==slide_id),None)
    if slide is None: raise ContractError(f"Unknown slide: {slide_id}")
    charts={c["chart_id"]:c for c in read_json(root/"charts.json")}
    content={c["content_id"]:c for c in read_json(root/"content.json").get("items",[])}
    copy=resolve_copy(slide,content)
    panels=[{"component_type":charts[c]["component_type"],"label":charts[c].get("display_title",""),"data":load_dataset(root,charts[c])} for c in slide.get("chart_ids",[])]
    candidates=[]
    for layout in manifest["layouts"]:
        for variant in layout["variants"]:
            if fits_layout(layout,panels,variant): continue
            limits=manifest["copy_limits"]
            if width_units(copy["action_title"])>limits["title_width_units"]: continue
            if width_units(copy["subtitle"])>limits["subtitle_width_units"]: continue
            if width_units(copy["implication"])>limits["rail_implication_width_units" if variant=="rail" else "implication_width_units"]: continue
            if any(width_units(p["label"])>limits["panel_title_width_units"] or any(width_units(c)>limits["category_width_units"] for c in p["data"]["categories"]) for p in panels): continue
            fingerprint=f"{'single' if len(panels)==1 else 'dual' if len(panels)==2 else 'multiples'}-{variant}"
            score=2*int(slide.get("page_role") in layout["jobs"])+4*int(slide.get("layout_id")==layout["id"])
            tie=hashlib.sha256(f"{seed}:{slide_id}:{layout['id']}:{variant}".encode()).hexdigest()
            candidates.append({"layout_id":layout["id"],"variant":variant,"structure_fingerprint":fingerprint,"score":score,"tie":tie})
    result=[]; seen=set()
    for candidate in sorted(candidates,key=lambda c:(-c["score"],c["tie"])):
        if candidate["structure_fingerprint"] in seen: continue
        seen.add(candidate["structure_fingerprint"])
        result.append({k:v for k,v in candidate.items() if k!="tie"})
        if len(result)>=limit: break
    return {"slide_id":slide_id,"candidates":result,"note":"Never invent extra variants to meet a requested count. Same content and data remain canonical; render every shortlisted candidate before selection."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir"); parser.add_argument("slide_id")
    parser.add_argument("--seed",default="consulting-deck"); parser.add_argument("--limit",type=int,default=3)
    args=parser.parse_args()
    if not 1<=args.limit<=6: parser.error("limit must be 1–6")
    try: result=query(Path(args.project_dir).resolve(),args.slide_id,args.seed,args.limit)
    except (ContractError,KeyError,TypeError,AttributeError) as exc:
        print(json.dumps({"status":"failed","blockers":[str(exc)]},ensure_ascii=False)); return 1
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result["candidates"] else 1


if __name__=="__main__": raise SystemExit(main())
