"""Construction settings for spanning forests and stable sorting."""
import os
from accounting import ROOT

BATCH = "classics-graphs-v0.10"
REVISION = "design-v0.10"
os.environ["SPECLESSBENCH_CONSTRUCTION_BATCH"] = BATCH
os.environ["SPECLESSBENCH_CONSTRUCTION_REVISION"] = REVISION
os.environ["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"] = "halt_on_error=1"
CORE = ROOT / "benchmarks/tasks/graphsuite-core"
BUILD = ROOT / "_build" / BATCH
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE = "/home/yangfp/.opam/five/bin"
GROUPS = [
    ("apsp", "all-pairs-shortest-path",
     [("APSP-01",1,0),("APSP-02",2,0)], "L4"),
    ("scc", "strongly-connected-components",
     [("SCC-01",1,1),("SCC-02",2,1)], "L4"),
    ("search", "boyer-moore-search",
     [("BM-01",1,2),("BM-02",2,2)], "L4")
]
