"""Produce nonduplicated new-group costs and check all final construction assets."""
import gzip
import hashlib
import json
import shutil
from pathlib import Path
from algorithms_common import ROOT, CORE, BUILD, GROUPS, LEAN, COQC, FIVE
from accounting import AUDIT, append, now
from cost_attribution import effective_commands


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def lines(p): return [json.loads(s) for s in p.read_text().splitlines()] if p.exists() else []


def main():
    reg=json.loads((CORE/"groups.json").read_text()); meta=json.loads((CORE/"compcert/build.json").read_text())
    assert len(reg["groups"])==6 and len(meta["exports"])==18
    for row in reg["protected_files"]:
        assert sha(CORE/row["path"])==row["sha256"],row["path"]
    for row in meta["exports"]:
        assert sha(CORE/row["path"])==row["sha256"],row["path"]
    commands=effective_commands(); summaries=[]
    for g in reg["groups"]:
        name=g["family"]; gid=g["group_id"]
        report=json.loads((CORE/"evidence"/(name+".json")).read_text())
        assert report["unexpected_disagreements"]==0 and report["negative_distinguishing_inputs"]>0
        assert not report["final_proof_attempted"] and not report["clight_execution_tested"]
        prior=report["registry_sha256"]
        archive=AUDIT/"registries"/(prior+".json")
        saved=json.loads(archive.read_text()) if sha(CORE/"groups.json")!=prior else reg
        assert saved==reg,"Program/goal registry changed since differential tests; cannot reuse evidence"
        corpus=ROOT/report["corpus"]; assert sha(corpus)==report["corpus_sha256"]
        with gzip.open(corpus,"rt") as stream: cases=[json.loads(s) for s in stream]
        assert len(cases)==len({tuple(x) for x in cases})==report["case_count"]
        cost_path=AUDIT/"groups"/(gid+".json"); cost=json.loads(cost_path.read_text())
        owned=[x for x in commands if x["group_id"]==gid]
        envelopes=[x for x in owned if x.get("measurement_role")=="envelope"]
        uncovered=[x for x in owned if x.get("measurement_role")!="envelope" and not any(
            e["started_utc"]<=x["started_utc"] and x["ended_utc"]<=e["ended_utc"] for e in envelopes)]
        cost["nonduplicated_tool_wall_seconds"]=sum(x["wall_seconds"] for x in envelopes+uncovered)
        cost["cost_total_rule"]="all envelopes plus uncovered details, never nested detail costs twice"
        cost["one_record_per_implementation_group"]=True
        cost["semantic_contexts"]=2; cost["platform_instances"]=6
        cost["case_count"]=report["case_count"]; cost["program_executions"]=report["program_executions"]
        cost["validity_evaluations"]=report["validity_evaluations"]
        cost["accounting_completeness"]="local commands instrumented; shared authoring batch token attribution and remote inference memory gaps explicit"
        cost_path.write_text(json.dumps(cost,indent=2)+"\n")
        summaries.append({"group_id":gid,"family":name,"unique_inputs":report["case_count"],
            "program_executions":report["program_executions"],"validity_evaluations":report["validity_evaluations"],
            "duplicates_removed":report["duplicate_inputs_removed"],"negative_inputs":report["negative_distinguishing_inputs"],
            "unexpected_disagreements":0,"tool_wall_seconds":cost["nonduplicated_tool_wall_seconds"],
            "max_process_rss_bytes":cost["max_process_rss_bytes"],"cost_record":cost_path.relative_to(ROOT).as_posix()})
    errors=lines(AUDIT/"issues.jsonl"); ids={r["id"] for r in errors}
    if "CMD-89448896ad77-resolution" not in ids:
        append(AUDIT/"issues.jsonl",{"schema_version":1,"timestamp_utc":now(),"id":"CMD-89448896ad77-resolution",
            "resolves":"CMD-89448896ad77","status":"resolved","kind":"resolution",
            "description":"Rename Lean reserved matches/prefix; revision9d36a1926de1; all six groups type-check and full differential tests pass",
            "revision":"design-v0.3.1","repair":"benchmarks/construction/repairs/9d36a1926de1/revision.json"})
    summary={"schema_version":1,"revision":"design-v0.3.1","timestamp_utc":now(),"implementation_groups":6,
        "semantic_contexts":12,"platform_instances":36,"clight_ast_count":18,"groups":summaries,
        "unique_inputs":sum(x["unique_inputs"] for x in summaries),"program_executions":sum(x["program_executions"] for x in summaries),
        "validity_evaluations":sum(x["validity_evaluations"] for x in summaries),
        "unexpected_disagreements":0,"final_proof_attempted":False,"labels_certified":False,
        "source_registry_sha256":sha(CORE/"groups.json"),"compcert_build_sha256":sha(CORE/"compcert/build.json"),
        "tools_at_audit":[{"path":str(p),"sha256":sha(Path(p))} for p in (LEAN,COQC,FIVE+"/clightgen",FIVE+"/coqc",shutil.which("gcc"),shutil.which("ocamlopt"))],
        "generator_dependencies":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in
             (ROOT/"scripts/construction/differential_algorithms.py",ROOT/"scripts/construction/algorithms_common.py")],
        "shared_usage_batch":"batch-algorithms-v0.3.json","exact_process_tree_peak_bytes":None,"hosted_inference_memory_bytes":None}
    shared=[x for x in commands if x["group_id"].startswith("shared") and x.get("batch_id")=="algorithms-v0.3"]
    summary["shared_tool_wall_seconds"]=sum(x["wall_seconds"] for x in shared)
    summary["shared_max_process_rss_bytes"]=max((x["max_process_rss_bytes"] or 0 for x in shared),default=None)
    summary["cost_events_complete_through"]=max((x["ended_utc"] for x in commands),default=None)
    (AUDIT/"summary-algorithms-v0.3.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({k:summary[k] for k in ("implementation_groups","semantic_contexts","platform_instances","unique_inputs","program_executions","validity_evaluations")}))

if __name__=="__main__": main()
