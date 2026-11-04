From SpecLessBenchSystems Require Import SystemsDomain Execution.

From SpecLessBenchSystems.Generated Require Import LEASES_V0.

Definition impl_LEASES_V0 : implementation :=
 {| program := LEASES_V0.prog; input_symbol := LEASES_V0._eb_input; output_symbol := LEASES_V0._eb_output |}.

From SpecLessBenchSystems.Generated Require Import LEASES_V1.

Definition impl_LEASES_V1 : implementation :=
 {| program := LEASES_V1.prog; input_symbol := LEASES_V1._eb_input; output_symbol := LEASES_V1._eb_output |}.

From SpecLessBenchSystems.Generated Require Import LEASES_V2.

Definition impl_LEASES_V2 : implementation :=
 {| program := LEASES_V2.prog; input_symbol := LEASES_V2._eb_input; output_symbol := LEASES_V2._eb_output |}.

Definition T_LEASE_WHEEL_equivalence : Prop := Equivalent (SystemsDomain.valid 2) SystemsDomain.encode impl_LEASES_V0 impl_LEASES_V1.

Definition T_LEASE_WHEEL_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 2) SystemsDomain.encode impl_LEASES_V0 impl_LEASES_V1 x oa ob.

Definition T_LEASE_STALE_equivalence : Prop := Equivalent (SystemsDomain.valid 2) SystemsDomain.encode impl_LEASES_V0 impl_LEASES_V2.

Definition T_LEASE_STALE_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 2) SystemsDomain.encode impl_LEASES_V0 impl_LEASES_V2 x oa ob.
