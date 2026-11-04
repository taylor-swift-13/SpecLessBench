From SpecLessBenchGraphSuite Require Import GraphSuiteDomain Execution.

From SpecLessBenchGraphSuite.Generated Require Import APSP_V0.

Definition impl_APSP_V0 : implementation :=
 {| program := APSP_V0.prog; input_symbol := APSP_V0._eb_input; output_symbol := APSP_V0._eb_output |}.

From SpecLessBenchGraphSuite.Generated Require Import APSP_V1.

Definition impl_APSP_V1 : implementation :=
 {| program := APSP_V1.prog; input_symbol := APSP_V1._eb_input; output_symbol := APSP_V1._eb_output |}.

From SpecLessBenchGraphSuite.Generated Require Import APSP_V2.

Definition impl_APSP_V2 : implementation :=
 {| program := APSP_V2.prog; input_symbol := APSP_V2._eb_input; output_symbol := APSP_V2._eb_output |}.

Definition APSP_01_equivalence : Prop := Equivalent (GraphSuiteDomain.valid 0) GraphSuiteDomain.encode impl_APSP_V0 impl_APSP_V1.

Definition APSP_01_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid 0) GraphSuiteDomain.encode impl_APSP_V0 impl_APSP_V1 x oa ob.

Definition APSP_02_equivalence : Prop := Equivalent (GraphSuiteDomain.valid 0) GraphSuiteDomain.encode impl_APSP_V0 impl_APSP_V2.

Definition APSP_02_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid 0) GraphSuiteDomain.encode impl_APSP_V0 impl_APSP_V2 x oa ob.
