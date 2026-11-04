(* Protected fixed program bindings. Generated ASTs are required.
 * No Parameters/Axioms stand in for missing implementations. *)
From EqualBench.QCIP Require Import Domain Execution.
From EqualBench.QCIP.Generated Require Import AVL_V0.
From EqualBench.QCIP.Generated Require Import AVL_V1.
From EqualBench.QCIP.Generated Require Import AVL_V2.
From EqualBench.QCIP.Generated Require Import AVL_V3.
Definition impl_AVL_V0 : implementation :=
  {| program := AVL_V0.prog; input_symbol := AVL_V0._eb_input;
     output_symbol := AVL_V0._eb_output |}.
Definition impl_AVL_V1 : implementation :=
  {| program := AVL_V1.prog; input_symbol := AVL_V1._eb_input;
     output_symbol := AVL_V1._eb_output |}.
Definition impl_AVL_V2 : implementation :=
  {| program := AVL_V2.prog; input_symbol := AVL_V2._eb_input;
     output_symbol := AVL_V2._eb_output |}.
Definition impl_AVL_V3 : implementation :=
  {| program := AVL_V3.prog; input_symbol := AVL_V3._eb_input;
     output_symbol := AVL_V3._eb_output |}.
