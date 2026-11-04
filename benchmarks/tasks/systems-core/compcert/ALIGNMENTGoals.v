From EqualBenchSystems Require Import SystemsDomain Execution.

From EqualBenchSystems.Generated Require Import ALIGNMENT_V0.

Definition impl_ALIGNMENT_V0 : implementation :=
 {| program := ALIGNMENT_V0.prog; input_symbol := ALIGNMENT_V0._eb_input; output_symbol := ALIGNMENT_V0._eb_output |}.

From EqualBenchSystems.Generated Require Import ALIGNMENT_V1.

Definition impl_ALIGNMENT_V1 : implementation :=
 {| program := ALIGNMENT_V1.prog; input_symbol := ALIGNMENT_V1._eb_input; output_symbol := ALIGNMENT_V1._eb_output |}.

From EqualBenchSystems.Generated Require Import ALIGNMENT_V2.

Definition impl_ALIGNMENT_V2 : implementation :=
 {| program := ALIGNMENT_V2.prog; input_symbol := ALIGNMENT_V2._eb_input; output_symbol := ALIGNMENT_V2._eb_output |}.

Definition A_ALIGN_MINIMA_equivalence : Prop := Equivalent (SystemsDomain.valid 3) SystemsDomain.encode impl_ALIGNMENT_V0 impl_ALIGNMENT_V1.

Definition A_ALIGN_MINIMA_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 3) SystemsDomain.encode impl_ALIGNMENT_V0 impl_ALIGNMENT_V1 x oa ob.

Definition A_ALIGN_TIES_equivalence : Prop := Equivalent (SystemsDomain.valid 3) SystemsDomain.encode impl_ALIGNMENT_V0 impl_ALIGNMENT_V2.

Definition A_ALIGN_TIES_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 3) SystemsDomain.encode impl_ALIGNMENT_V0 impl_ALIGNMENT_V2 x oa ob.
