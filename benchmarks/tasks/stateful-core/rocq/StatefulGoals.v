From SpecLessBenchStatefulNative Require Import StatefulNative StatefulDomain.

Definition S_FRAME_RING_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid 0) (StatefulNative.entry 0 0) (StatefulNative.entry 0 1).

Definition S_FRAME_RING_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid 0) (StatefulNative.entry 0 0) (StatefulNative.entry 0 1) x oa ob.

Definition S_FRAME_EMPTY_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid 0) (StatefulNative.entry 0 0) (StatefulNative.entry 0 2).

Definition S_FRAME_EMPTY_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid 0) (StatefulNative.entry 0 0) (StatefulNative.entry 0 2) x oa ob.

Definition S_TX_JOURNAL_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid 1) (StatefulNative.entry 1 0) (StatefulNative.entry 1 1).

Definition S_TX_JOURNAL_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid 1) (StatefulNative.entry 1 0) (StatefulNative.entry 1 1) x oa ob.

Definition S_TX_COMMIT_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid 1) (StatefulNative.entry 1 0) (StatefulNative.entry 1 2).

Definition S_TX_COMMIT_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid 1) (StatefulNative.entry 1 0) (StatefulNative.entry 1 2) x oa ob.

Definition S_LRU_LINKS_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid 2) (StatefulNative.entry 2 0) (StatefulNative.entry 2 1).

Definition S_LRU_LINKS_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid 2) (StatefulNative.entry 2 0) (StatefulNative.entry 2 1) x oa ob.

Definition S_LRU_TOUCH_equivalence : Prop := StatefulNative.Equivalent (StatefulDomain.valid 2) (StatefulNative.entry 2 0) (StatefulNative.entry 2 2).

Definition S_LRU_TOUCH_refutationAt (x oa ob : StatefulNative.words) : Prop := StatefulNative.RefutationAt (StatefulDomain.valid 2) (StatefulNative.entry 2 0) (StatefulNative.entry 2 2) x oa ob.
