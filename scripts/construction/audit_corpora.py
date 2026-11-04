"""Count records versus distinct inputs without rewriting historical reports."""
import gzip
import hashlib
import json
from accounting import ROOT, AUDIT, now


def main():
    records=[]
    for family in ("bst","avl","ring","dijkstra"):
        path=ROOT/"benchmarks/tasks/qcip-core/evidence"/(family+"-three-platform.json")
        report=json.loads(path.read_text()); corpus=ROOT/report["corpus"]
        assert hashlib.sha256(corpus.read_bytes()).hexdigest()==report["corpus_sha256"]
        with gzip.open(corpus,"rt") as stream:
            keys=[json.dumps(json.loads(line),sort_keys=True,separators=(",",":")) for line in stream]
        assert len(keys)==report["case_count"]
        records.append({"group_id":report["group_id"],"input_records":len(keys),"unique_inputs":len(set(keys)),
            "duplicate_records":len(keys)-len(set(keys)),"historical_report_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "corpus_sha256":report["corpus_sha256"]})
    out={"schema_version":1,"timestamp_utc":now(),"scope":"historical QCIP differential corpora; no mutation of reports",
        "groups":records,"input_records":sum(r["input_records"] for r in records),
        "unique_inputs":sum(r["unique_inputs"] for r in records)}
    (AUDIT/"corpus-audit-qcip-v0.2.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out))

if __name__=="__main__": main()
