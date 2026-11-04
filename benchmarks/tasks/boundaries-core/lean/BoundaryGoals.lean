import BoundaryDomain
namespace SpecLessBenchBoundary
def C_TREE_STACK_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def C_TREE_STACK_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def C_TREE_SUBTREE_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def C_TREE_SUBTREE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
def C_UF_HALVING_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 1)
def C_UF_HALVING_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 1) x oa ob
def C_UF_ONEHOP_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 2)
def C_UF_ONEHOP_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 2) x oa ob
def C_PQ_REP_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 1)
def C_PQ_REP_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 1) x oa ob
def C_PQ_CHILD_equivalence : Prop := Equivalent (valid 3) (entry 2 0) (entry 2 2)
def C_PQ_CHILD_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 3) (entry 2 0) (entry 2 2) x oa ob
def C_EVAL_DP_equivalence : Prop := Equivalent (valid 4) (entry 3 0) (entry 3 1)
def C_EVAL_DP_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 4) (entry 3 0) (entry 3 1) x oa ob
def C_EVAL_SHORTCIRCUIT_equivalence : Prop := Equivalent (valid 4) (entry 3 0) (entry 3 2)
def C_EVAL_SHORTCIRCUIT_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 4) (entry 3 0) (entry 3 2) x oa ob
def B_TLV_CURSOR_equivalence : Prop := Equivalent (valid 5) (entry 4 0) (entry 4 1)
def B_TLV_CURSOR_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 5) (entry 4 0) (entry 4 1) x oa ob
def B_TLV_ENDIAN_equivalence : Prop := Equivalent (valid 5) (entry 4 0) (entry 4 2)
def B_TLV_ENDIAN_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 5) (entry 4 0) (entry 4 2) x oa ob
def B_QUOTE_SPANS_equivalence : Prop := Equivalent (valid 6) (entry 5 0) (entry 5 1)
def B_QUOTE_SPANS_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 6) (entry 5 0) (entry 5 1) x oa ob
def B_QUOTE_EMPTY_equivalence : Prop := Equivalent (valid 6) (entry 5 0) (entry 5 2)
def B_QUOTE_EMPTY_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 6) (entry 5 0) (entry 5 2) x oa ob
def B_PACK_SUFFIX_equivalence : Prop := Equivalent (valid 7) (entry 6 0) (entry 6 1)
def B_PACK_SUFFIX_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 7) (entry 6 0) (entry 6 1) x oa ob
def B_PACK_REPEAT_equivalence : Prop := Equivalent (valid 7) (entry 6 0) (entry 6 2)
def B_PACK_REPEAT_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 7) (entry 6 0) (entry 6 2) x oa ob
def B_PATH_REVERSE_equivalence : Prop := Equivalent (valid 8) (entry 7 0) (entry 7 1)
def B_PATH_REVERSE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 8) (entry 7 0) (entry 7 1) x oa ob
def B_PATH_PARENTS_equivalence : Prop := Equivalent (valid 8) (entry 7 0) (entry 7 2)
def B_PATH_PARENTS_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 8) (entry 7 0) (entry 7 2) x oa ob
end SpecLessBenchBoundary
