"""Toolchain and stable group identifiers for the systems tranche."""
import os
from accounting import ROOT

BATCH = "systems-v0.6"
REVISION = "design-v0.6.2"
os.environ["EQUALBENCH_CONSTRUCTION_BATCH"] = BATCH
os.environ["EQUALBENCH_CONSTRUCTION_REVISION"] = REVISION
os.environ["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"] = "halt_on_error=1"
CORE = ROOT / "benchmarks/tasks/systems-core"
BUILD = ROOT / "_build" / BATCH
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE = "/home/yangfp/.opam/five/bin"
GROUPS = [
    ("graph", "dependency-invalidation",
     [("G-INVALIDATE-WORKLIST", 1, 0), ("G-INVALIDATE-DIRTY", 2, 0)], "L3-L4"),
    ("scopes", "scoped-bindings",
     [("N-SCOPE-OVERLAY", 1, 1), ("N-SCOPE-TOMBSTONE", 2, 1)], "L2-L3"),
    ("leases", "lease-expiration",
     [("T-LEASE-WHEEL", 1, 2), ("T-LEASE-STALE", 2, 2)], "L3-L4"),
    ("alignment", "banded-affine-alignment",
     [("A-ALIGN-MINIMA", 1, 3), ("A-ALIGN-TIES", 2, 3)], "L4"),
    ("resample", "fixed-point-resampling",
     [("A-RESAMPLE-PHASE", 1, 4), ("A-RESAMPLE-HALF", 2, 4)], "L3"),
]
