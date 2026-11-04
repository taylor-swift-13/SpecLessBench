"""Build settings for a Base64 reference and two alternatives."""
import os
from accounting import ROOT
BATCH = "base64-v0.7"
REVISION = "design-v0.7"
os.environ["EQUALBENCH_CONSTRUCTION_BATCH"] = BATCH
os.environ["EQUALBENCH_CONSTRUCTION_REVISION"] = REVISION
os.environ["ASAN_OPTIONS"] = "detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"] = "halt_on_error=1"
CORE = ROOT / "benchmarks/tasks/base64-core"
BUILD = ROOT / "_build" / BATCH
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE = "/home/yangfp/.opam/five/bin"
GROUPS = [("base64","base64-encoding",[("A-BASE64-STREAM",1,0),("A-BASE64-PADDING",2,0)],"L3")]
