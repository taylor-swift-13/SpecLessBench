import ClassicsDomain
namespace SpecLessBenchClassics
def MST_TIED_WEIGHT_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def MST_TIED_WEIGHT_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def MST_UNIQUE_EDGES_equivalence : Prop := Equivalent (valid 1) (entry 0 0) (entry 0 1)
def MST_UNIQUE_EDGES_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 0 0) (entry 0 1) x oa ob
def MST_MAX_COUNTEREXAMPLE_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def MST_MAX_COUNTEREXAMPLE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
def SORT_MERGE_equivalence : Prop := Equivalent (valid 2) (entry 1 0) (entry 1 1)
def SORT_MERGE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 1 0) (entry 1 1) x oa ob
def SORT_UNSTABLE_equivalence : Prop := Equivalent (valid 2) (entry 1 0) (entry 1 2)
def SORT_UNSTABLE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 1 0) (entry 1 2) x oa ob
end SpecLessBenchClassics
