"""Observable contract tests; no network or PowerPoint application required."""
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from exhibit_contracts import ContractError, compile_workspace, file_hash, load_dataset, local_path, resolve_copy
from verify_chart_data import verify
from query_native_layouts import query
import finalize_gate

MANIFEST = Path(__file__).resolve().parents[1] / "assets/layouts/native-exhibits.json"


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def fixture(root):
    data = {"categories":["IT","知识管理","营销"],"unit":"%","value_scale":"percent-points",
            "series":[{"id":"scaled","name":"规模化","values":[32,20,12]},{"id":"other","name":"其他","values":[68,80,88]}]}
    dump(root/"data/chart.json",data)
    chart = {"chart_id":"CH1","slide_id":"S1","component_type":"survey","data_path":"data/chart.json","unit":"%","source_locator":"Public report, p.4"}
    dump(root/"charts.json",[chart])
    dump(root/"slides.json",[{"slide_id":"S1","layout_id":"C40","chart_ids":["CH1"],"content_bindings":{"action_title":"T","implication":"I"}}])
    dump(root/"content.json",{"items":[{"content_id":"T","text":"AI规模化程度在职能之间存在差异"},{"content_id":"I","text":"先在高成熟度职能验证，再扩展到其他职能。"}]})
    return data,chart


def pptx_fixture(path, data, workbook_delta=0, cache_delta=0, external=False):
    # A minimal package is sufficient to exercise the data reconciler, not a
    # deliverable deck. End-to-end export tests use the actual native runtime.
    p="http://schemas.openxmlformats.org/presentationml/2006/main"
    r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    c="http://schemas.openxmlformats.org/drawingml/2006/chart"
    s="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    def rel(target, mode=""):
        return f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Target="{target}" {mode}/></Relationships>'
    cells = []
    for index,name in enumerate(["类别"]+[s["name"] for s in data["series"]]):
        column=chr(65+index)
        cells.append(f'<c r="{column}1" t="inlineStr"><is><t>{escape(name)}</t></is></c>')
    rows=[f'<row r="1">{"".join(cells)}</row>']
    for i,name in enumerate(data["categories"],2):
        cells=[f'<c r="A{i}" t="inlineStr"><is><t>{escape(name)}</t></is></c>']
        for j,series in enumerate(data["series"],1):
            value=series["values"][i-2]/100 + (workbook_delta if i==2 and j==1 else 0)
            cells.append(f'<c r="{chr(65+j)}{i}"><v>{value}</v></c>')
        rows.append(f'<row r="{i}">{"".join(cells)}</row>')
    workbook=io.BytesIO()
    with zipfile.ZipFile(workbook,"w") as z:
        z.writestr("xl/workbook.xml",f'<workbook xmlns="{s}" xmlns:r="{r}"><sheets><sheet name="数据" r:id="r1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",rel("worksheets/sheet1.xml"))
        z.writestr("xl/worksheets/sheet1.xml",f'<worksheet xmlns="{s}"><sheetData>{"".join(rows)}</sheetData></worksheet>')
    series_xml=[]
    def cache(values):
        return ''.join(f'<c:pt idx="{i}"><c:v>{escape(str(v))}</c:v></c:pt>' for i,v in enumerate(values))
    for i,series in enumerate(data["series"]):
        col=chr(66+i)
        values=[v/100 + (cache_delta if i==0 and j==0 else 0) for j,v in enumerate(series["values"])]
        n=len(values)+1
        series_xml.append(f'''<c:ser><c:tx><c:strRef><c:f>'数据'!${col}$1</c:f><c:strCache>{cache([series['name']])}</c:strCache></c:strRef></c:tx>
          <c:cat><c:strRef><c:f>'数据'!$A$2:$A${n}</c:f><c:strCache>{cache(data['categories'])}</c:strCache></c:strRef></c:cat>
          <c:val><c:numRef><c:f>'数据'!${col}$2:${col}${n}</c:f><c:numCache>{cache(values)}</c:numCache></c:numRef></c:val></c:ser>''')
    with zipfile.ZipFile(path,"w") as z:
        z.writestr("ppt/presentation.xml",f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId r:id="r1"/></p:sldIdLst></p:presentation>')
        z.writestr("ppt/_rels/presentation.xml.rels",rel("slides/slide1.xml"))
        z.writestr("ppt/slides/slide1.xml",f'<p:sld xmlns:p="{p}" xmlns:c="{c}" xmlns:r="{r}"><c:chart r:id="r1"/></p:sld>')
        z.writestr("ppt/slides/_rels/slide1.xml.rels",rel("../charts/chart1.xml"))
        z.writestr("ppt/charts/chart1.xml",f'<c:chartSpace xmlns:c="{c}" xmlns:r="{r}"><c:chart><c:plotArea><c:barChart>{"".join(series_xml)}</c:barChart><c:valAx><c:numFmt formatCode="0%"/></c:valAx></c:plotArea></c:chart><c:externalData r:id="r1"/></c:chartSpace>')
        z.writestr("ppt/charts/_rels/chart1.xml.rels",rel("../embeddings/data.xlsx",'TargetMode="External"' if external else ""))
        z.writestr("ppt/embeddings/data.xlsx",workbook.getvalue())


class Contracts(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.data,self.chart=fixture(self.root)
    def tearDown(self):
        self.tmp.cleanup()
    def test_compile_preserves_original_values(self):
        plan=compile_workspace(self.root,MANIFEST)
        self.assertEqual(plan["slides"][0]["panels"][0]["data"],self.data)
        self.assertIn("data/chart.json",plan["source_hashes"])
    def test_chart_ownership_cannot_be_duplicated(self):
        dump(self.root/"slides.json",[{"slide_id":"S1","layout_id":"C42","chart_ids":["CH1","CH1"],"action_title":"比较两个图表"}])
        with self.assertRaisesRegex(ContractError,"exactly once"):
            compile_workspace(self.root,MANIFEST)
    def test_small_multiples_share_percent_range_and_ticks(self):
        dump(self.root/"charts.json",[{**self.chart,"chart_id":f"CH{i}","component_type":"column"} for i in range(3)])
        dump(self.root/"slides.json",[{"slide_id":"S1","layout_id":"C43","chart_ids":[f"CH{i}" for i in range(3)],"action_title":"使用共同尺度比较各组"}])
        plan=compile_workspace(self.root,MANIFEST)
        self.assertEqual({(p["axis_min"],p["axis_max"],p["axis_major_unit"]) for p in plan["slides"][0]["panels"]},{(0,1,.2)})
    def test_bound_title_changes_in_all_variants(self):
        contents={"T":{"text":"新结论"}}
        for variant in ("wide","rail"):
            self.assertEqual(resolve_copy({"selected_variant":variant,"content_bindings":{"action_title":"T"}},contents)["action_title"],"新结论")
    def test_duplicate_business_copy_rejected(self):
        with self.assertRaises(ContractError):
            resolve_copy({"action_title":"旧结论","content_bindings":{"action_title":"T"}},{"T":{"text":"新结论"}})
    def test_paths_escape_and_symlinks_rejected(self):
        with self.assertRaises(ContractError): local_path(self.root,"../secret.json")
        (self.root/"outside").symlink_to(self.root.parent)
        with self.assertRaises(ContractError): local_path(self.root,"outside/secret.json")
    def test_missing_nan_and_length_mismatch_rejected(self):
        for values in ([None,20,12],[float('nan'),20,12],[32,20]):
            data=copy.deepcopy(self.data); data["series"][0]["values"]=values
            dump(self.root/"data/chart.json",data)
            with self.assertRaises(ContractError): load_dataset(self.root,self.chart)
    def test_percent_scale_and_unit_mismatch_rejected(self):
        for update in ({"value_scale":"raw"},{"unit":"亿元"}):
            dump(self.root/"data/chart.json",{**self.data,**update})
            with self.assertRaises(ContractError): load_dataset(self.root,self.chart)
    def test_rounded_stack_kept_not_normalized(self):
        self.data["series"][1]["values"][0]=67
        dump(self.root/"data/chart.json",self.data)
        self.assertEqual(load_dataset(self.root,self.chart)["series"][1]["values"][0],67)
        self.data["series"][1]["values"][0]=50
        dump(self.root/"data/chart.json",self.data)
        with self.assertRaises(ContractError): load_dataset(self.root,self.chart)
    def test_long_chinese_and_too_many_categories_rejected(self):
        content={"items":[{"content_id":"T","text":"超过页面容量的完整中文标题"*8},{"content_id":"I","text":"含义"}]}
        dump(self.root/"content.json",content)
        with self.assertRaises(ContractError): compile_workspace(self.root,MANIFEST)
        fixture(self.root)
        self.data['categories']=[str(i) for i in range(13)]
        for series in self.data['series']: series['values']=[50]*13
        dump(self.root/'data/chart.json',self.data)
        with self.assertRaises(ContractError): compile_workspace(self.root,MANIFEST)
    def test_layout_query_reproducible_and_genuinely_distinct(self):
        first=query(self.root,'S1','same-seed',3)
        self.assertEqual(first,query(self.root,'S1','same-seed',3))
        fingerprints=[c['structure_fingerprint'] for c in first['candidates']]
        self.assertEqual(len(fingerprints),len(set(fingerprints)))
        self.assertEqual(len(fingerprints),2)
    def test_csv_needs_explicit_mapping_and_no_blank_zero(self):
        csv_path=self.root/"data/data.csv"; csv_path.write_text("category,value\nA,1\nB,\n",encoding="utf-8")
        chart={**self.chart,"data_path":"data/data.csv","csv_mapping":{"category":"category","series":[{"id":"s","name":"s","column":"value"}]}}
        with self.assertRaises(ContractError): load_dataset(self.root,chart)
    def contract(self):
        return {"source_hashes":{"data/chart.json":file_hash(self.root/"data/chart.json")},"slides":[{"slide_number":1,"charts":[{"chart_id":"CH1","chart_order":1,"categories":self.data["categories"],"series":[{"name":s["name"],"values":[v/100 for v in s["values"]]} for s in self.data["series"]],"require_workbook":True,"number_format":"0%"}]}]}
    def test_cache_and_workbook_reconcile(self):
        path=self.root/"deck.pptx"; pptx_fixture(path,self.data)
        report=verify(path,self.contract(),self.root)
        self.assertTrue(report["passed"],report["blockers"])
        self.assertTrue(report["charts"][0]["workbook_reconciled"])
    def test_wrong_workbook_cache_external_and_stale_source_block(self):
        path=self.root/"deck.pptx"
        for args in ({"workbook_delta":.01},{"cache_delta":.01},{"external":True}):
            pptx_fixture(path,self.data,**args)
            self.assertFalse(verify(path,self.contract(),self.root)["passed"])
        pptx_fixture(path,self.data); contract=self.contract()
        dump(self.root/"data/chart.json",{**self.data,"note":"changed"})
        self.assertFalse(verify(path,contract,self.root)["passed"])
    def test_empty_machine_reports_never_pass(self):
        qa=self.root/"qa"
        dump(qa/"project-validation.json",{}); dump(qa/"pptx-inspection.json",{})
        dump(qa/"manual-review.json",{k:True for k in finalize_gate.REQUIRED_MANUAL_CHECKS})
        dump(self.root/"brief.json",{})
        previous=sys.argv; sys.argv=["finalize_gate",str(self.root)]
        try:
            with contextlib.redirect_stdout(io.StringIO()): code=finalize_gate.main()
        finally: sys.argv=previous
        self.assertEqual(code,1)
        self.assertFalse(json.loads((qa/"final-gate.json").read_text())["passed"])

    def test_failed_or_contradictory_reports_never_pass(self):
        qa=self.root/"qa"
        dump(qa/"manual-review.json",{k:True for k in finalize_gate.REQUIRED_MANUAL_CHECKS})
        dump(self.root/"brief.json",{})
        for report in ({"status":"failed","blockers":[]}, {"status":"passed","blockers":["bad"]}, {"status":"passed","warnings":"bad"}):
            dump(qa/"project-validation.json",report)
            dump(qa/"pptx-inspection.json",{"status":"passed","blockers":[],"warnings":[]})
            previous=sys.argv;sys.argv=["finalize_gate",str(self.root)]
            try:
                with contextlib.redirect_stdout(io.StringIO()):code=finalize_gate.main()
            finally:sys.argv=previous
            self.assertEqual(code,1,report)

    def test_gate_rejects_stale_or_incomplete_component_reports(self):
        qa=self.root/"qa";pptx=self.root/"deck.pptx";pptx_fixture(pptx,self.data)
        dump(self.root/"brief.json",{"native_component_contract":1})
        hashes={"data/chart.json":file_hash(self.root/"data/chart.json")}
        project={"status":"passed","blockers":[],"warnings":[],"source_hashes":hashes}
        inspection={"status":"passed","blockers":[],"warnings":[],"file":str(pptx),"native_chart_count":1,"pptx_sha256":file_hash(pptx)}
        report=verify(pptx,self.contract(),self.root)
        dump(qa/"manual-review.json",{k:True for k in finalize_gate.REQUIRED_MANUAL_CHECKS})
        dump(qa/"project-validation.json",project);dump(qa/"pptx-inspection.json",inspection)
        for update,expected in (({},0),({"pptx_sha256":"old"},1),({"charts":[]},1),({"charts":[{"status":"passed"}]},1)):
            dump(qa/"chart-validation.json",{**report,**update})
            previous=sys.argv;sys.argv=["finalize_gate",str(self.root)]
            try:
                with contextlib.redirect_stdout(io.StringIO()):code=finalize_gate.main()
            finally:sys.argv=previous
            self.assertEqual(code,expected,update)
        dump(qa/"chart-validation.json",report)
        dump(self.root/"data/chart.json",{**self.data,"note":"changed"})
        previous=sys.argv;sys.argv=["finalize_gate",str(self.root)]
        try:
            with contextlib.redirect_stdout(io.StringIO()):code=finalize_gate.main()
        finally:sys.argv=previous
        self.assertEqual(code,1)


if __name__=="__main__": unittest.main()
