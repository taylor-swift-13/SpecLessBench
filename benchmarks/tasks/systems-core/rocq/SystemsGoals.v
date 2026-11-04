From SpecLessBenchSystemsNative Require Import SystemsNative SystemsDomain.

Definition G_INVALIDATE_WORKLIST_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 0) (SystemsNative.entry 0 0) (SystemsNative.entry 0 1).

Definition G_INVALIDATE_WORKLIST_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 0) (SystemsNative.entry 0 0) (SystemsNative.entry 0 1) x oa ob.

Definition G_INVALIDATE_DIRTY_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 0) (SystemsNative.entry 0 0) (SystemsNative.entry 0 2).

Definition G_INVALIDATE_DIRTY_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 0) (SystemsNative.entry 0 0) (SystemsNative.entry 0 2) x oa ob.

Definition N_SCOPE_OVERLAY_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 1) (SystemsNative.entry 1 0) (SystemsNative.entry 1 1).

Definition N_SCOPE_OVERLAY_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 1) (SystemsNative.entry 1 0) (SystemsNative.entry 1 1) x oa ob.

Definition N_SCOPE_TOMBSTONE_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 1) (SystemsNative.entry 1 0) (SystemsNative.entry 1 2).

Definition N_SCOPE_TOMBSTONE_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 1) (SystemsNative.entry 1 0) (SystemsNative.entry 1 2) x oa ob.

Definition T_LEASE_WHEEL_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 2) (SystemsNative.entry 2 0) (SystemsNative.entry 2 1).

Definition T_LEASE_WHEEL_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 2) (SystemsNative.entry 2 0) (SystemsNative.entry 2 1) x oa ob.

Definition T_LEASE_STALE_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 2) (SystemsNative.entry 2 0) (SystemsNative.entry 2 2).

Definition T_LEASE_STALE_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 2) (SystemsNative.entry 2 0) (SystemsNative.entry 2 2) x oa ob.

Definition A_ALIGN_MINIMA_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 3) (SystemsNative.entry 3 0) (SystemsNative.entry 3 1).

Definition A_ALIGN_MINIMA_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 3) (SystemsNative.entry 3 0) (SystemsNative.entry 3 1) x oa ob.

Definition A_ALIGN_TIES_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 3) (SystemsNative.entry 3 0) (SystemsNative.entry 3 2).

Definition A_ALIGN_TIES_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 3) (SystemsNative.entry 3 0) (SystemsNative.entry 3 2) x oa ob.

Definition A_RESAMPLE_PHASE_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 4) (SystemsNative.entry 4 0) (SystemsNative.entry 4 1).

Definition A_RESAMPLE_PHASE_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 4) (SystemsNative.entry 4 0) (SystemsNative.entry 4 1) x oa ob.

Definition A_RESAMPLE_HALF_equivalence : Prop := SystemsNative.Equivalent (SystemsDomain.valid 4) (SystemsNative.entry 4 0) (SystemsNative.entry 4 2).

Definition A_RESAMPLE_HALF_refutationAt (x oa ob : SystemsNative.words) : Prop := SystemsNative.RefutationAt (SystemsDomain.valid 4) (SystemsNative.entry 4 0) (SystemsNative.entry 4 2) x oa ob.
