From EqualBenchSystems Require Import SystemsDomain Execution.

From EqualBenchSystems.Generated Require Import RESAMPLE_V0.

Definition impl_RESAMPLE_V0 : implementation :=
 {| program := RESAMPLE_V0.prog; input_symbol := RESAMPLE_V0._eb_input; output_symbol := RESAMPLE_V0._eb_output |}.

From EqualBenchSystems.Generated Require Import RESAMPLE_V1.

Definition impl_RESAMPLE_V1 : implementation :=
 {| program := RESAMPLE_V1.prog; input_symbol := RESAMPLE_V1._eb_input; output_symbol := RESAMPLE_V1._eb_output |}.

From EqualBenchSystems.Generated Require Import RESAMPLE_V2.

Definition impl_RESAMPLE_V2 : implementation :=
 {| program := RESAMPLE_V2.prog; input_symbol := RESAMPLE_V2._eb_input; output_symbol := RESAMPLE_V2._eb_output |}.

Definition A_RESAMPLE_PHASE_equivalence : Prop := Equivalent (SystemsDomain.valid 4) SystemsDomain.encode impl_RESAMPLE_V0 impl_RESAMPLE_V1.

Definition A_RESAMPLE_PHASE_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 4) SystemsDomain.encode impl_RESAMPLE_V0 impl_RESAMPLE_V1 x oa ob.

Definition A_RESAMPLE_HALF_equivalence : Prop := Equivalent (SystemsDomain.valid 4) SystemsDomain.encode impl_RESAMPLE_V0 impl_RESAMPLE_V2.

Definition A_RESAMPLE_HALF_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 4) SystemsDomain.encode impl_RESAMPLE_V0 impl_RESAMPLE_V2 x oa ob.
