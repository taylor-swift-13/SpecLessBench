From SpecLessBenchGraphSuite Require Import GraphSuiteDomain Execution.

From SpecLessBenchGraphSuite.Generated Require Import SEARCH_V0.

Definition impl_SEARCH_V0 : implementation :=
 {| program := SEARCH_V0.prog; input_symbol := SEARCH_V0._eb_input; output_symbol := SEARCH_V0._eb_output |}.

From SpecLessBenchGraphSuite.Generated Require Import SEARCH_V1.

Definition impl_SEARCH_V1 : implementation :=
 {| program := SEARCH_V1.prog; input_symbol := SEARCH_V1._eb_input; output_symbol := SEARCH_V1._eb_output |}.

From SpecLessBenchGraphSuite.Generated Require Import SEARCH_V2.

Definition impl_SEARCH_V2 : implementation :=
 {| program := SEARCH_V2.prog; input_symbol := SEARCH_V2._eb_input; output_symbol := SEARCH_V2._eb_output |}.

Definition BM_01_equivalence : Prop := Equivalent (GraphSuiteDomain.valid 2) GraphSuiteDomain.encode impl_SEARCH_V0 impl_SEARCH_V1.

Definition BM_01_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid 2) GraphSuiteDomain.encode impl_SEARCH_V0 impl_SEARCH_V1 x oa ob.

Definition BM_02_equivalence : Prop := Equivalent (GraphSuiteDomain.valid 2) GraphSuiteDomain.encode impl_SEARCH_V0 impl_SEARCH_V2.

Definition BM_02_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid 2) GraphSuiteDomain.encode impl_SEARCH_V0 impl_SEARCH_V2 x oa ob.
