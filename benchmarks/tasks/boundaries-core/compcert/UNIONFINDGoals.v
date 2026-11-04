From EqualBenchBoundary Require Import BoundaryDomain Execution.

From EqualBenchBoundary.Generated Require Import UNIONFIND_V0.

Definition impl_UNIONFIND_V0 : implementation :=
 {| program := UNIONFIND_V0.prog; input_symbol := UNIONFIND_V0._eb_input; output_symbol := UNIONFIND_V0._eb_output |}.

From EqualBenchBoundary.Generated Require Import UNIONFIND_V1.

Definition impl_UNIONFIND_V1 : implementation :=
 {| program := UNIONFIND_V1.prog; input_symbol := UNIONFIND_V1._eb_input; output_symbol := UNIONFIND_V1._eb_output |}.

From EqualBenchBoundary.Generated Require Import UNIONFIND_V2.

Definition impl_UNIONFIND_V2 : implementation :=
 {| program := UNIONFIND_V2.prog; input_symbol := UNIONFIND_V2._eb_input; output_symbol := UNIONFIND_V2._eb_output |}.

Definition C_UF_HALVING_equivalence : Prop := Equivalent (BoundaryDomain.valid 1) BoundaryDomain.encode impl_UNIONFIND_V0 impl_UNIONFIND_V1.

Definition C_UF_HALVING_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 1) BoundaryDomain.encode impl_UNIONFIND_V0 impl_UNIONFIND_V1 x oa ob.

Definition C_UF_ONEHOP_equivalence : Prop := Equivalent (BoundaryDomain.valid 1) BoundaryDomain.encode impl_UNIONFIND_V0 impl_UNIONFIND_V2.

Definition C_UF_ONEHOP_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 1) BoundaryDomain.encode impl_UNIONFIND_V0 impl_UNIONFIND_V2 x oa ob.
