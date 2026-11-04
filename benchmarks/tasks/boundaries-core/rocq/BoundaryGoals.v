From EqualBenchBoundaryNative Require Import BoundaryNative BoundaryDomain.

Definition C_TREE_STACK_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 0) (BoundaryNative.entry 0 0) (BoundaryNative.entry 0 1).

Definition C_TREE_STACK_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 0) (BoundaryNative.entry 0 0) (BoundaryNative.entry 0 1) x oa ob.

Definition C_TREE_SUBTREE_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 0) (BoundaryNative.entry 0 0) (BoundaryNative.entry 0 2).

Definition C_TREE_SUBTREE_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 0) (BoundaryNative.entry 0 0) (BoundaryNative.entry 0 2) x oa ob.

Definition C_UF_HALVING_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 1) (BoundaryNative.entry 1 0) (BoundaryNative.entry 1 1).

Definition C_UF_HALVING_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 1) (BoundaryNative.entry 1 0) (BoundaryNative.entry 1 1) x oa ob.

Definition C_UF_ONEHOP_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 1) (BoundaryNative.entry 1 0) (BoundaryNative.entry 1 2).

Definition C_UF_ONEHOP_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 1) (BoundaryNative.entry 1 0) (BoundaryNative.entry 1 2) x oa ob.

Definition C_PQ_REP_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 2) (BoundaryNative.entry 2 0) (BoundaryNative.entry 2 1).

Definition C_PQ_REP_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 2) (BoundaryNative.entry 2 0) (BoundaryNative.entry 2 1) x oa ob.

Definition C_PQ_CHILD_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 3) (BoundaryNative.entry 2 0) (BoundaryNative.entry 2 2).

Definition C_PQ_CHILD_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 3) (BoundaryNative.entry 2 0) (BoundaryNative.entry 2 2) x oa ob.

Definition C_EVAL_DP_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 4) (BoundaryNative.entry 3 0) (BoundaryNative.entry 3 1).

Definition C_EVAL_DP_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 4) (BoundaryNative.entry 3 0) (BoundaryNative.entry 3 1) x oa ob.

Definition C_EVAL_SHORTCIRCUIT_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 4) (BoundaryNative.entry 3 0) (BoundaryNative.entry 3 2).

Definition C_EVAL_SHORTCIRCUIT_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 4) (BoundaryNative.entry 3 0) (BoundaryNative.entry 3 2) x oa ob.

Definition B_TLV_CURSOR_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 5) (BoundaryNative.entry 4 0) (BoundaryNative.entry 4 1).

Definition B_TLV_CURSOR_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 5) (BoundaryNative.entry 4 0) (BoundaryNative.entry 4 1) x oa ob.

Definition B_TLV_ENDIAN_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 5) (BoundaryNative.entry 4 0) (BoundaryNative.entry 4 2).

Definition B_TLV_ENDIAN_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 5) (BoundaryNative.entry 4 0) (BoundaryNative.entry 4 2) x oa ob.

Definition B_QUOTE_SPANS_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 6) (BoundaryNative.entry 5 0) (BoundaryNative.entry 5 1).

Definition B_QUOTE_SPANS_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 6) (BoundaryNative.entry 5 0) (BoundaryNative.entry 5 1) x oa ob.

Definition B_QUOTE_EMPTY_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 6) (BoundaryNative.entry 5 0) (BoundaryNative.entry 5 2).

Definition B_QUOTE_EMPTY_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 6) (BoundaryNative.entry 5 0) (BoundaryNative.entry 5 2) x oa ob.

Definition B_PACK_SUFFIX_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 7) (BoundaryNative.entry 6 0) (BoundaryNative.entry 6 1).

Definition B_PACK_SUFFIX_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 7) (BoundaryNative.entry 6 0) (BoundaryNative.entry 6 1) x oa ob.

Definition B_PACK_REPEAT_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 7) (BoundaryNative.entry 6 0) (BoundaryNative.entry 6 2).

Definition B_PACK_REPEAT_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 7) (BoundaryNative.entry 6 0) (BoundaryNative.entry 6 2) x oa ob.

Definition B_PATH_REVERSE_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 8) (BoundaryNative.entry 7 0) (BoundaryNative.entry 7 1).

Definition B_PATH_REVERSE_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 8) (BoundaryNative.entry 7 0) (BoundaryNative.entry 7 1) x oa ob.

Definition B_PATH_PARENTS_equivalence : Prop := BoundaryNative.Equivalent (BoundaryDomain.valid 8) (BoundaryNative.entry 7 0) (BoundaryNative.entry 7 2).

Definition B_PATH_PARENTS_refutationAt (x oa ob : BoundaryNative.words) : Prop := BoundaryNative.RefutationAt (BoundaryDomain.valid 8) (BoundaryNative.entry 7 0) (BoundaryNative.entry 7 2) x oa ob.
