"""Three stateful groups; no final target proofs during construction."""
import os
from accounting import ROOT
os.environ['SPECLESSBENCH_CONSTRUCTION_BATCH']='stateful-v0.5'
os.environ['SPECLESSBENCH_CONSTRUCTION_REVISION']='design-v0.5.1'
os.environ['ASAN_OPTIONS']='detect_leaks=0:halt_on_error=1'
os.environ['UBSAN_OPTIONS']='halt_on_error=1'
CORE=ROOT/'benchmarks/tasks/stateful-core'
BUILD=ROOT/'_build/stateful-v0.5'
LEAN='/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean'
COQC='/home/yangfp/.opam/qcp-8.20/bin/coqc'
FIVE='/home/yangfp/.opam/five/bin'
GROUPS=[
 ('frames','incremental-frame-stream',[('S-FRAME-RING',1,0),('S-FRAME-EMPTY',2,0)],'L3-L4'),
 ('transactions','nested-transaction-store',[('S-TX-JOURNAL',1,1),('S-TX-COMMIT',2,1)],'L3-L4'),
 ('lru','intrusive-lru-cache',[('S-LRU-LINKS',1,2),('S-LRU-TOUCH',2,2)],'L3-L4')]
