From SpecLessBenchGraphSuite Require Import GraphSuiteDomain Execution.

From SpecLessBenchGraphSuite.Generated Require Import SCC_V0.

Definition impl_SCC_V0 : implementation :=
 {| program := SCC_V0.prog; input_symbol := SCC_V0._eb_input; output_symbol := SCC_V0._eb_output |}.

From SpecLessBenchGraphSuite.Generated Require Import SCC_V1.

Definition impl_SCC_V1 : implementation :=
 {| program := SCC_V1.prog; input_symbol := SCC_V1._eb_input; output_symbol := SCC_V1._eb_output |}.

From SpecLessBenchGraphSuite.Generated Require Import SCC_V2.

Definition impl_SCC_V2 : implementation :=
 {| program := SCC_V2.prog; input_symbol := SCC_V2._eb_input; output_symbol := SCC_V2._eb_output |}.

Definition SCC_01_equivalence : Prop := Equivalent (GraphSuiteDomain.valid 1) GraphSuiteDomain.encode impl_SCC_V0 impl_SCC_V1.

Definition SCC_01_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid 1) GraphSuiteDomain.encode impl_SCC_V0 impl_SCC_V1 x oa ob.

Definition SCC_02_equivalence : Prop := Equivalent (GraphSuiteDomain.valid 1) GraphSuiteDomain.encode impl_SCC_V0 impl_SCC_V2.

Definition SCC_02_refutationAt (x : GraphSuiteDomain.words) (oa ob : observation) : Prop := RefutationAt (GraphSuiteDomain.valid 1) GraphSuiteDomain.encode impl_SCC_V0 impl_SCC_V2 x oa ob.
