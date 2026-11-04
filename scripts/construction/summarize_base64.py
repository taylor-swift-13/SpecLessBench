"""Audit the Base64 source bindings, corpus and group-level costs."""
import gzip
import hashlib
import json
from base64_common import CORE, GROUPS, REVISION, ROOT
from accounting import AUDIT, now
from cost_attribution import effective_commands


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    registry=json.loads((CORE/"groups.json").read_text())
    build=json.loads((CORE/"compcert/build.json").read_text())
    report=json.loads((CORE/"evidence/base64.json").read_text())
    assert len(build["exports"])==3
    for item in registry["protected_files"]+build["exports"]:
        assert sha(CORE/item["path"])==item["sha256"]
    assert report["registry_sha256"]==sha(CORE/"groups.json")
    assert report["fixtures_sha256"]==sha(CORE/"fixtures.json")
    assert report["generator_sha256"]==sha(ROOT/"scripts/construction/differential_base64.py")
    assert report["corpus_generator_sha256"]==sha(ROOT/"scripts/construction/base64_cases.py")
    assert not report["unexpected_disagreements"] and report["negative_distinguishing_inputs"]>0
    assert not report["final_proof_attempted"] and not report["clight_execution_tested"]
    corpus=ROOT/report["corpus"]
    assert sha(corpus)==report["corpus_sha256"]
    with gzip.open(corpus,"rt") as stream:
        cases=[json.loads(line) for line in stream]
    assert len(cases)==len({tuple(case) for case in cases})==report["case_count"]
    assert report["cases_by_origin"]["source"]==7
    commands=effective_commands()
    gid=GROUPS[0][1]
    owned=[row for row in commands if row["group_id"]==gid]
    envelopes=[row for row in owned if row.get("measurement_role")=="envelope"]
    uncovered=[row for row in owned if row.get("measurement_role")!="envelope" and not any(
        env["started_utc"]<=row["started_utc"] and row["ended_utc"]<=env["ended_utc"] for env in envelopes)]
    cost_path=AUDIT/"groups"/(gid+".json")
    cost=json.loads(cost_path.read_text())
    cost["nonduplicated_tool_wall_seconds"]=sum(row["wall_seconds"] for row in envelopes+uncovered)
    cost["case_count"]=len(cases)
    cost["program_executions"]=report["program_executions"]
    cost["cost_total_rule"]="envelopes plus uncovered details, without multiplying by tasks or platforms"
    cost_path.write_text(json.dumps(cost,indent=2)+"\n")
    group={"group_id":gid,"family":"base64","unique_inputs":len(cases),
           "program_executions":report["program_executions"],"validity_evaluations":report["validity_evaluations"],
           "negative_inputs":report["negative_distinguishing_inputs"],"source_derived_inputs":7,
           "unexpected_disagreements":0,"cost_record":cost_path.relative_to(ROOT).as_posix()}
    summary={"schema_version":1,"revision":REVISION,"timestamp_utc":now(),"implementation_groups":1,
             "semantic_contexts":2,"platform_instances":6,"clight_ast_count":3,"groups":[group],
             "unique_inputs":len(cases),"program_executions":report["program_executions"],
             "validity_evaluations":report["validity_evaluations"],"unexpected_disagreements":0,
             "labels_certified":False,"final_proof_attempted":False,"source_registry_sha256":sha(CORE/"groups.json"),
             "fixtures_sha256":sha(CORE/"fixtures.json"),"shared_usage_batch":"batch-base64-v0.7.json",
             "exact_process_tree_peak_bytes":None,"hosted_inference_memory_bytes":None}
    (AUDIT/"summary-base64-v0.7.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({k:summary[k] for k in ("implementation_groups","semantic_contexts","unique_inputs","program_executions")}))


if __name__=="__main__":
    main()
