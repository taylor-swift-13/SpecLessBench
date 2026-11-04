"""Boundary-rich programs plus data-structure controls; no final proofs."""
import os
from accounting import ROOT
os.environ["EQUALBENCH_CONSTRUCTION_BATCH"]="boundaries-v0.4"
os.environ["EQUALBENCH_CONSTRUCTION_REVISION"]="design-v0.4"
os.environ["ASAN_OPTIONS"]="detect_leaks=0:halt_on_error=1"
os.environ["UBSAN_OPTIONS"]="halt_on_error=1"
CORE=ROOT/"benchmarks/tasks/boundaries-core"
BUILD=ROOT/"_build/boundaries-v0.4"
LEAN="/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC="/home/yangfp/.opam/qcp-8.20/bin/coqc"
FIVE="/home/yangfp/.opam/five/bin"
# family, cost/split group, contexts (ID,right variant,domain), provisional level
GROUPS=[
 ("tree","pointer-tree-mirror",[("C-TREE-STACK",1,0),("C-TREE-SUBTREE",2,0)],"L3"),
 ("unionfind","union-find-connectivity",[("C-UF-HALVING",1,1),("C-UF-ONEHOP",2,1)],"L3"),
 ("priority","max-priority-queue",[("C-PQ-REP",1,2),("C-PQ-CHILD",2,3)],"L3"),
 ("eval","tagged-evaluator",[("C-EVAL-DP",1,4),("C-EVAL-SHORTCIRCUIT",2,4)],"L4"),
 ("tlv","binary-tlv-decoder",[("B-TLV-CURSOR",1,5),("B-TLV-ENDIAN",2,5)],"L3"),
 ("quotes","quoted-tokenizer",[("B-QUOTE-SPANS",1,6),("B-QUOTE-EMPTY",2,6)],"L2-L3"),
 ("packbits","packbits-decoder",[("B-PACK-SUFFIX",1,7),("B-PACK-REPEAT",2,7)],"L3"),
 ("path","lexical-path-normalizer",[("B-PATH-REVERSE",1,8),("B-PATH-PARENTS",2,8)],"L3"),
]
