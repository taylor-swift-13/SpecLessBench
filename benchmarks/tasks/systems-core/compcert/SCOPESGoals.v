From EqualBenchSystems Require Import SystemsDomain Execution.

From EqualBenchSystems.Generated Require Import SCOPES_V0.

Definition impl_SCOPES_V0 : implementation :=
 {| program := SCOPES_V0.prog; input_symbol := SCOPES_V0._eb_input; output_symbol := SCOPES_V0._eb_output |}.

From EqualBenchSystems.Generated Require Import SCOPES_V1.

Definition impl_SCOPES_V1 : implementation :=
 {| program := SCOPES_V1.prog; input_symbol := SCOPES_V1._eb_input; output_symbol := SCOPES_V1._eb_output |}.

From EqualBenchSystems.Generated Require Import SCOPES_V2.

Definition impl_SCOPES_V2 : implementation :=
 {| program := SCOPES_V2.prog; input_symbol := SCOPES_V2._eb_input; output_symbol := SCOPES_V2._eb_output |}.

Definition N_SCOPE_OVERLAY_equivalence : Prop := Equivalent (SystemsDomain.valid 1) SystemsDomain.encode impl_SCOPES_V0 impl_SCOPES_V1.

Definition N_SCOPE_OVERLAY_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 1) SystemsDomain.encode impl_SCOPES_V0 impl_SCOPES_V1 x oa ob.

Definition N_SCOPE_TOMBSTONE_equivalence : Prop := Equivalent (SystemsDomain.valid 1) SystemsDomain.encode impl_SCOPES_V0 impl_SCOPES_V2.

Definition N_SCOPE_TOMBSTONE_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 1) SystemsDomain.encode impl_SCOPES_V0 impl_SCOPES_V2 x oa ob.
