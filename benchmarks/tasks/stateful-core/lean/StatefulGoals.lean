import StatefulDomain
namespace SpecLessBenchStateful
def S_FRAME_RING_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def S_FRAME_RING_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def S_FRAME_EMPTY_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def S_FRAME_EMPTY_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
def S_TX_JOURNAL_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 1)
def S_TX_JOURNAL_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 1) x oa ob
def S_TX_COMMIT_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 2)
def S_TX_COMMIT_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 2) x oa ob
def S_LRU_LINKS_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 1)
def S_LRU_LINKS_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 1) x oa ob
def S_LRU_TOUCH_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 2)
def S_LRU_TOUCH_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 2) x oa ob
end SpecLessBenchStateful
