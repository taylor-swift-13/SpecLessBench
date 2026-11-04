From EqualBenchBoundary Require Import BoundaryDomain Execution.

From EqualBenchBoundary.Generated Require Import PACKBITS_V0.

Definition impl_PACKBITS_V0 : implementation :=
 {| program := PACKBITS_V0.prog; input_symbol := PACKBITS_V0._eb_input; output_symbol := PACKBITS_V0._eb_output |}.

From EqualBenchBoundary.Generated Require Import PACKBITS_V1.

Definition impl_PACKBITS_V1 : implementation :=
 {| program := PACKBITS_V1.prog; input_symbol := PACKBITS_V1._eb_input; output_symbol := PACKBITS_V1._eb_output |}.

From EqualBenchBoundary.Generated Require Import PACKBITS_V2.

Definition impl_PACKBITS_V2 : implementation :=
 {| program := PACKBITS_V2.prog; input_symbol := PACKBITS_V2._eb_input; output_symbol := PACKBITS_V2._eb_output |}.

Definition B_PACK_SUFFIX_equivalence : Prop := Equivalent (BoundaryDomain.valid 7) BoundaryDomain.encode impl_PACKBITS_V0 impl_PACKBITS_V1.

Definition B_PACK_SUFFIX_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 7) BoundaryDomain.encode impl_PACKBITS_V0 impl_PACKBITS_V1 x oa ob.

Definition B_PACK_REPEAT_equivalence : Prop := Equivalent (BoundaryDomain.valid 7) BoundaryDomain.encode impl_PACKBITS_V0 impl_PACKBITS_V2.

Definition B_PACK_REPEAT_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 7) BoundaryDomain.encode impl_PACKBITS_V0 impl_PACKBITS_V2 x oa ob.
