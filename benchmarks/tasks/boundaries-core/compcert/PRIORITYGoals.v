From EqualBenchBoundary Require Import BoundaryDomain Execution.

From EqualBenchBoundary.Generated Require Import PRIORITY_V0.

Definition impl_PRIORITY_V0 : implementation :=
 {| program := PRIORITY_V0.prog; input_symbol := PRIORITY_V0._eb_input; output_symbol := PRIORITY_V0._eb_output |}.

From EqualBenchBoundary.Generated Require Import PRIORITY_V1.

Definition impl_PRIORITY_V1 : implementation :=
 {| program := PRIORITY_V1.prog; input_symbol := PRIORITY_V1._eb_input; output_symbol := PRIORITY_V1._eb_output |}.

From EqualBenchBoundary.Generated Require Import PRIORITY_V2.

Definition impl_PRIORITY_V2 : implementation :=
 {| program := PRIORITY_V2.prog; input_symbol := PRIORITY_V2._eb_input; output_symbol := PRIORITY_V2._eb_output |}.

Definition C_PQ_REP_equivalence : Prop := Equivalent (BoundaryDomain.valid 2) BoundaryDomain.encode impl_PRIORITY_V0 impl_PRIORITY_V1.

Definition C_PQ_REP_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 2) BoundaryDomain.encode impl_PRIORITY_V0 impl_PRIORITY_V1 x oa ob.

Definition C_PQ_CHILD_equivalence : Prop := Equivalent (BoundaryDomain.valid 3) BoundaryDomain.encode impl_PRIORITY_V0 impl_PRIORITY_V2.

Definition C_PQ_CHILD_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 3) BoundaryDomain.encode impl_PRIORITY_V0 impl_PRIORITY_V2 x oa ob.
