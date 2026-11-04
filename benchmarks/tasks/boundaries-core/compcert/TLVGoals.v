From EqualBenchBoundary Require Import BoundaryDomain Execution.

From EqualBenchBoundary.Generated Require Import TLV_V0.

Definition impl_TLV_V0 : implementation :=
 {| program := TLV_V0.prog; input_symbol := TLV_V0._eb_input; output_symbol := TLV_V0._eb_output |}.

From EqualBenchBoundary.Generated Require Import TLV_V1.

Definition impl_TLV_V1 : implementation :=
 {| program := TLV_V1.prog; input_symbol := TLV_V1._eb_input; output_symbol := TLV_V1._eb_output |}.

From EqualBenchBoundary.Generated Require Import TLV_V2.

Definition impl_TLV_V2 : implementation :=
 {| program := TLV_V2.prog; input_symbol := TLV_V2._eb_input; output_symbol := TLV_V2._eb_output |}.

Definition B_TLV_CURSOR_equivalence : Prop := Equivalent (BoundaryDomain.valid 5) BoundaryDomain.encode impl_TLV_V0 impl_TLV_V1.

Definition B_TLV_CURSOR_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 5) BoundaryDomain.encode impl_TLV_V0 impl_TLV_V1 x oa ob.

Definition B_TLV_ENDIAN_equivalence : Prop := Equivalent (BoundaryDomain.valid 5) BoundaryDomain.encode impl_TLV_V0 impl_TLV_V2.

Definition B_TLV_ENDIAN_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 5) BoundaryDomain.encode impl_TLV_V0 impl_TLV_V2 x oa ob.
