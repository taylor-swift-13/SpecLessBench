From SpecLessBenchGraphSuiteNative Require Import GraphSuiteNative GraphSuiteDomain.

Definition APSP_01_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid 0) (GraphSuiteNative.entry 0 0) (GraphSuiteNative.entry 0 1).

Definition APSP_01_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid 0) (GraphSuiteNative.entry 0 0) (GraphSuiteNative.entry 0 1) x oa ob.

Definition APSP_02_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid 0) (GraphSuiteNative.entry 0 0) (GraphSuiteNative.entry 0 2).

Definition APSP_02_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid 0) (GraphSuiteNative.entry 0 0) (GraphSuiteNative.entry 0 2) x oa ob.

Definition SCC_01_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid 1) (GraphSuiteNative.entry 1 0) (GraphSuiteNative.entry 1 1).

Definition SCC_01_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid 1) (GraphSuiteNative.entry 1 0) (GraphSuiteNative.entry 1 1) x oa ob.

Definition SCC_02_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid 1) (GraphSuiteNative.entry 1 0) (GraphSuiteNative.entry 1 2).

Definition SCC_02_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid 1) (GraphSuiteNative.entry 1 0) (GraphSuiteNative.entry 1 2) x oa ob.

Definition BM_01_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid 2) (GraphSuiteNative.entry 2 0) (GraphSuiteNative.entry 2 1).

Definition BM_01_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid 2) (GraphSuiteNative.entry 2 0) (GraphSuiteNative.entry 2 1) x oa ob.

Definition BM_02_equivalence : Prop := GraphSuiteNative.Equivalent (GraphSuiteDomain.valid 2) (GraphSuiteNative.entry 2 0) (GraphSuiteNative.entry 2 2).

Definition BM_02_refutationAt (x oa ob : GraphSuiteNative.words) : Prop := GraphSuiteNative.RefutationAt (GraphSuiteDomain.valid 2) (GraphSuiteNative.entry 2 0) (GraphSuiteNative.entry 2 2) x oa ob.
