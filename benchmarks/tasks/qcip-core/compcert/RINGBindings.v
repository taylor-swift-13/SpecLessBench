(* Protected fixed program bindings. Generated ASTs are required.
 * No Parameters/Axioms stand in for missing implementations. *)
From SpecLessBench.QCIP Require Import Domain Execution.
From SpecLessBench.QCIP.Generated Require Import RING_V0.
From SpecLessBench.QCIP.Generated Require Import RING_V1.
From SpecLessBench.QCIP.Generated Require Import RING_V2.
From SpecLessBench.QCIP.Generated Require Import RING_V3.
Definition impl_RING_V0 : implementation :=
  {| program := RING_V0.prog; input_symbol := RING_V0._eb_input;
     output_symbol := RING_V0._eb_output |}.
Definition impl_RING_V1 : implementation :=
  {| program := RING_V1.prog; input_symbol := RING_V1._eb_input;
     output_symbol := RING_V1._eb_output |}.
Definition impl_RING_V2 : implementation :=
  {| program := RING_V2.prog; input_symbol := RING_V2._eb_input;
     output_symbol := RING_V2._eb_output |}.
Definition impl_RING_V3 : implementation :=
  {| program := RING_V3.prog; input_symbol := RING_V3._eb_input;
     output_symbol := RING_V3._eb_output |}.
