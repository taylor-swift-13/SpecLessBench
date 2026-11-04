From EqualBenchClassicsNative Require Import ClassicsNative ClassicsDomain.

Definition MST_TIED_WEIGHT_equivalence : Prop := ClassicsNative.Equivalent (ClassicsDomain.valid 0) (ClassicsNative.entry 0 0) (ClassicsNative.entry 0 1).

Definition MST_TIED_WEIGHT_refutationAt (x oa ob : ClassicsNative.words) : Prop := ClassicsNative.RefutationAt (ClassicsDomain.valid 0) (ClassicsNative.entry 0 0) (ClassicsNative.entry 0 1) x oa ob.

Definition MST_UNIQUE_EDGES_equivalence : Prop := ClassicsNative.Equivalent (ClassicsDomain.valid 1) (ClassicsNative.entry 0 0) (ClassicsNative.entry 0 1).

Definition MST_UNIQUE_EDGES_refutationAt (x oa ob : ClassicsNative.words) : Prop := ClassicsNative.RefutationAt (ClassicsDomain.valid 1) (ClassicsNative.entry 0 0) (ClassicsNative.entry 0 1) x oa ob.

Definition MST_MAX_COUNTEREXAMPLE_equivalence : Prop := ClassicsNative.Equivalent (ClassicsDomain.valid 0) (ClassicsNative.entry 0 0) (ClassicsNative.entry 0 2).

Definition MST_MAX_COUNTEREXAMPLE_refutationAt (x oa ob : ClassicsNative.words) : Prop := ClassicsNative.RefutationAt (ClassicsDomain.valid 0) (ClassicsNative.entry 0 0) (ClassicsNative.entry 0 2) x oa ob.

Definition SORT_MERGE_equivalence : Prop := ClassicsNative.Equivalent (ClassicsDomain.valid 2) (ClassicsNative.entry 1 0) (ClassicsNative.entry 1 1).

Definition SORT_MERGE_refutationAt (x oa ob : ClassicsNative.words) : Prop := ClassicsNative.RefutationAt (ClassicsDomain.valid 2) (ClassicsNative.entry 1 0) (ClassicsNative.entry 1 1) x oa ob.

Definition SORT_UNSTABLE_equivalence : Prop := ClassicsNative.Equivalent (ClassicsDomain.valid 2) (ClassicsNative.entry 1 0) (ClassicsNative.entry 1 2).

Definition SORT_UNSTABLE_refutationAt (x oa ob : ClassicsNative.words) : Prop := ClassicsNative.RefutationAt (ClassicsDomain.valid 2) (ClassicsNative.entry 1 0) (ClassicsNative.entry 1 2) x oa ob.
