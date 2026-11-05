"""One active inventory across construction batches; no duplicated group charges."""
import hashlib
import json
from accounting import ROOT,AUDIT,now

def main():
    old_path=AUDIT/"summary-qcip-v0.2.json"
    if not old_path.exists():
        old=json.loads((AUDIT/"summary.json").read_text())
        assert old["implementation_groups"]==4
        old_path.write_text(json.dumps(old,indent=2)+"\n")
    old=json.loads(old_path.read_text()); new=json.loads((AUDIT/"summary-algorithms-v0.3.json").read_text())
    audit=json.loads((AUDIT/"corpus-audit-qcip-v0.2.json").read_text())
    old_registry=ROOT/"benchmarks/tasks/qcip-core/three-platform.json"
    new_registry=ROOT/"benchmarks/tasks/algorithms-core/groups.json"
    registries=[old_registry,new_registry]; batches=[old,new]; names=[old_path.name,"summary-algorithms-v0.3.json"]
    boundary_summary=AUDIT/"summary-boundaries-v0.4.json"
    if boundary_summary.exists():
        batches.append(json.loads(boundary_summary.read_text()));names.append(boundary_summary.name)
        registries.append(ROOT/"benchmarks/tasks/boundaries-core/groups.json")
    stateful_summary=AUDIT/"summary-stateful-v0.5.json"
    if stateful_summary.exists():
        batches.append(json.loads(stateful_summary.read_text()));names.append(stateful_summary.name)
        registries.append(ROOT/"benchmarks/tasks/stateful-core/groups.json")
    systems_summary=AUDIT/"summary-systems-v0.6.json"
    if systems_summary.exists():
        batches.append(json.loads(systems_summary.read_text()));names.append(systems_summary.name)
        registries.append(ROOT/"benchmarks/tasks/systems-core/groups.json")
    base64_summary=AUDIT/"summary-base64-v0.7.json"
    if base64_summary.exists():
        batches.append(json.loads(base64_summary.read_text()));names.append(base64_summary.name)
        registries.append(ROOT/"benchmarks/tasks/base64-core/groups.json")
    classics_summary=AUDIT/"summary-classics-v0.8.json"
    if classics_summary.exists():
        batches.append(json.loads(classics_summary.read_text()));names.append(classics_summary.name)
        registries.append(ROOT/"benchmarks/tasks/classics-core/groups.json")
    graphsuite_summary=AUDIT/"summary-graphsuite-v0.10.json"
    if graphsuite_summary.exists():
        batches.append(json.loads(graphsuite_summary.read_text()));names.append(graphsuite_summary.name)
        registries.append(ROOT/"benchmarks/tasks/graphsuite-core/groups.json")
    countsort_summary=AUDIT/"summary-countsort-v0.11.json"
    if countsort_summary.exists():
        batches.append(json.loads(countsort_summary.read_text()));names.append(countsort_summary.name)
        registries.append(ROOT/"benchmarks/tasks/countsort-core/groups.json")
    policy_path=ROOT/"benchmarks/split-family-policy.json"
    split_policy=json.loads(policy_path.read_text()) if policy_path.exists() else {"canonical_group_aliases":{}}
    aliases=split_policy["canonical_group_aliases"]
    groups=[]
    for p in registries:
        reg=json.loads(p.read_text())
        for g in reg["groups"]:
            ids=[t.get("context_id",t.get("id")) for t in g["tasks"]]
            original_split=g.get("split_group_id",g["group_id"])
            groups.append({"group_id":g["group_id"],"split_group_id":aliases.get(original_split,original_split),"source_split_group_id":original_split,"contexts":ids,"platforms":["lean","rocq","compcert"],
                "source_registry":p.relative_to(ROOT).as_posix(),"cost_record":"benchmarks/construction/groups/"+g["group_id"]+".json"})
    assert len({g["group_id"] for g in groups})==len(groups)==sum(b["implementation_groups"]for b in batches)
    contexts=[c for g in groups for c in g["contexts"]]; assert len(set(contexts))==len(contexts)==sum(b["semantic_contexts"]for b in batches)
    asts=sum(b["clight_ast_count"]if "clight_ast_count"in b else len(b["compcert"]["exports"])for b in batches)
    entries=22+(4 if boundary_summary.exists()else 0)+(3 if stateful_summary.exists()else 0)+(5 if systems_summary.exists()else 0)+(1 if base64_summary.exists()else 0)+(2 if classics_summary.exists()else 0)+(2 if graphsuite_summary.exists()else 0)
    slots=54+(8 if boundary_summary.exists()else 0)+(6 if stateful_summary.exists()else 0)+(10 if systems_summary.exists()else 0)+(2 if base64_summary.exists()else 0)+(5 if classics_summary.exists()else 0)+(6 if graphsuite_summary.exists()else 0)+(2 if countsort_summary.exists()else 0)
    active={"schema_version":1,"updated_utc":now(),"groups":groups,"implementation_groups":len(groups),
        "semantic_contexts":len(contexts),"platform_instances":3*len(contexts),"clight_ast_count":asts,
        "catalog_entries":entries,"catalog_context_slots":slots,"remaining_candidate_slots":slots-len(contexts),
        "catalog_count_scope":"versioned plan entries/slots, not independent family or released-task counts",
        "final_proofs_required_at_construction":False,"reference_certified_contexts":0}
    if policy_path.exists():
        active["split_policy"]="benchmarks/split-family-policy.json"
        active["split_policy_sha256"]=hashlib.sha256(policy_path.read_bytes()).hexdigest()
    interface=ROOT/"benchmarks/proof-interface/manifest.json"
    if interface.exists():
        active["proof_acceptance_contract"]="benchmarks/proof-interface/manifest.json"
        active["proof_acceptance_contract_sha256"]=hashlib.sha256(interface.read_bytes()).hexdigest()
        active["bare_logical_disjunction_is_sufficient"]=False
        active["literal_counterexample_data_required"]=True
    (ROOT/"benchmarks/active-groups.json").write_text(json.dumps(active,indent=2)+"\n")
    total={"schema_version":2,"updated_utc":now(),"implementation_groups":len(groups),"semantic_contexts":len(contexts),
        "platform_instances":3*len(contexts),"clight_ast_count":asts,"groups":[g for b in batches for g in b["groups"]],
        "input_records":old["total_family_inputs"]+sum(b["unique_inputs"]for b in batches[1:]),
        "unique_inputs":audit["unique_inputs"]+sum(b["unique_inputs"]for b in batches[1:]),
        "program_executions":old["total_program_executions"]+sum(b["program_executions"]for b in batches[1:]),
        "domain_evaluations_after_qcip":sum(b["validity_evaluations"]for b in batches[1:]),"unexpected_differences":0,
        "labels_certified":False,"final_target_proofs_attempted":False,
        "shared_model_usage_batches":["batch-three-platform-v0.2.json","batch-algorithms-v0.3.json"]+(["batch-boundaries-v0.4.json"]if boundary_summary.exists()else [])+(["batch-stateful-v0.5.json"]if stateful_summary.exists()else [])+(["batch-systems-v0.6.json"]if systems_summary.exists()else [])+(["batch-base64-v0.7.json"]if base64_summary.exists()else []),
        "cost_aggregation":"each group once, shared batch once; never multiply by targets/platforms",
        "coverage_scope":"selected successful full/supplemental evidence; smoke and failed/repeated attempts are retained as costs, not additional unique coverage",
        "all_historical_costs_known":False,"exact_concurrent_tree_memory_known":False,
        "batch_summaries":names}
    if classics_summary.exists(): total["shared_model_usage_batches"].append("batch-classics-v0.8.json")
    if graphsuite_summary.exists(): total["shared_model_usage_batches"].append("batch-classics-graphs-v0.10.json")
    if countsort_summary.exists(): total["shared_model_usage_batches"].append("batch-construction-continuation-v0.11.json")
    if interface.exists():
        total["proof_acceptance_contract"]="benchmarks/proof-interface/manifest.json"
        total["proof_acceptance_contract_sha256"]=hashlib.sha256(interface.read_bytes()).hexdigest()
        total["submission_interface_validation"]=json.loads((interface.parent/"validation.json").read_text())
    (AUDIT/"summary.json").write_text(json.dumps(total,indent=2)+"\n")
    print(json.dumps({k:total[k] for k in ("implementation_groups","semantic_contexts","platform_instances","input_records","unique_inputs","program_executions")}))
    from summarize_total_cost import main as refresh_total_cost
    refresh_total_cost()

if __name__=="__main__": main()
