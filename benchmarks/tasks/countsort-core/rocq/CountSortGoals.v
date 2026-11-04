From SpecLessBenchCountSortNative Require Import CountSortNative CountSortDomain.

Definition COUNT_01_equivalence : Prop := CountSortNative.Equivalent (CountSortDomain.valid 0) (CountSortNative.entry 0 0) (CountSortNative.entry 0 1).

Definition COUNT_01_refutationAt (x oa ob : CountSortNative.words) : Prop := CountSortNative.RefutationAt (CountSortDomain.valid 0) (CountSortNative.entry 0 0) (CountSortNative.entry 0 1) x oa ob.

Definition COUNT_02_equivalence : Prop := CountSortNative.Equivalent (CountSortDomain.valid 0) (CountSortNative.entry 0 0) (CountSortNative.entry 0 2).

Definition COUNT_02_refutationAt (x oa ob : CountSortNative.words) : Prop := CountSortNative.RefutationAt (CountSortDomain.valid 0) (CountSortNative.entry 0 0) (CountSortNative.entry 0 2) x oa ob.
