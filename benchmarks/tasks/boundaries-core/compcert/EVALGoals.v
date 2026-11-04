From EqualBenchBoundary Require Import BoundaryDomain Execution.

From EqualBenchBoundary.Generated Require Import EVAL_V0.

Definition impl_EVAL_V0 : implementation :=
 {| program := EVAL_V0.prog; input_symbol := EVAL_V0._eb_input; output_symbol := EVAL_V0._eb_output |}.

From EqualBenchBoundary.Generated Require Import EVAL_V1.

Definition impl_EVAL_V1 : implementation :=
 {| program := EVAL_V1.prog; input_symbol := EVAL_V1._eb_input; output_symbol := EVAL_V1._eb_output |}.

From EqualBenchBoundary.Generated Require Import EVAL_V2.

Definition impl_EVAL_V2 : implementation :=
 {| program := EVAL_V2.prog; input_symbol := EVAL_V2._eb_input; output_symbol := EVAL_V2._eb_output |}.

Definition C_EVAL_DP_equivalence : Prop := Equivalent (BoundaryDomain.valid 4) BoundaryDomain.encode impl_EVAL_V0 impl_EVAL_V1.

Definition C_EVAL_DP_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 4) BoundaryDomain.encode impl_EVAL_V0 impl_EVAL_V1 x oa ob.

Definition C_EVAL_SHORTCIRCUIT_equivalence : Prop := Equivalent (BoundaryDomain.valid 4) BoundaryDomain.encode impl_EVAL_V0 impl_EVAL_V2.

Definition C_EVAL_SHORTCIRCUIT_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 4) BoundaryDomain.encode impl_EVAL_V0 impl_EVAL_V2 x oa ob.
