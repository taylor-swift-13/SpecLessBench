"""Configuration for the next six concrete groups (not a proof runner)."""
import os
from pathlib import Path
from accounting import ROOT
os.environ["EQUALBENCH_CONSTRUCTION_BATCH"] = "algorithms-v0.3"
os.environ["EQUALBENCH_CONSTRUCTION_REVISION"] = "design-v0.3.1"
os.environ["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"] = "halt_on_error=1"
CORE = ROOT / "benchmarks/tasks/algorithms-core"
BUILD = ROOT / "_build/algorithms-v0.3"
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE = "/home/yangfp/.opam/five/bin"
GROUPS = [
    ("factorial", "basic-factorial", "R-FAC", "L1", "W1"),
    ("reverse", "sequence-reversal", "R-REV", "L2", "W1"),
    ("sum", "sequence-sum", "R-SUM", "L1", "W1"),
    ("matrix", "matrix-product", "R-MAT", "L3", "W1"),
    ("search", "first-match-search", "R-STR", "L3-L4", "W2"),
    ("queue", "queue-traces", "R-QUE", "L2-L3", "W2"),
]
