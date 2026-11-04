"""Construction settings for spanning forests and stable sorting."""
import os
from accounting import ROOT

BATCH = "classics-v0.8"
REVISION = "design-v0.8.2"
os.environ["EQUALBENCH_CONSTRUCTION_BATCH"] = BATCH
os.environ["EQUALBENCH_CONSTRUCTION_REVISION"] = REVISION
os.environ["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"] = "halt_on_error=1"
CORE = ROOT / "benchmarks/tasks/classics-core"
BUILD = ROOT / "_build" / BATCH
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE = "/home/yangfp/.opam/five/bin"
GROUPS = [
    ("forest", "minimum-spanning-forest",
     [("MST-TIED-WEIGHT",1,0),("MST-UNIQUE-EDGES",1,1),("MST-MAX-COUNTEREXAMPLE",2,0)], "L4"),
    ("sorting", "stable-record-sorting",
     [("SORT-MERGE",1,2),("SORT-UNSTABLE",2,2)], "L3")
]
