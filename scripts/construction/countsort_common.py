"""Construction settings for spanning forests and stable sorting."""
import os
from accounting import ROOT

BATCH = "construction-continuation-v0.11"
REVISION = "design-v0.11"
os.environ["SPECLESSBENCH_CONSTRUCTION_BATCH"] = BATCH
os.environ["SPECLESSBENCH_CONSTRUCTION_REVISION"] = REVISION
os.environ["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"] = "halt_on_error=1"
CORE = ROOT / "benchmarks/tasks/countsort-core"
BUILD = ROOT / "_build" / BATCH
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE = "/home/yangfp/.opam/five/bin"
GROUPS = [("records", "stable-counting-sort",
           [("COUNT-01",1,0),("COUNT-02",2,0)], "L3")]
