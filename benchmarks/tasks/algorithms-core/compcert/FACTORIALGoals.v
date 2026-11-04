From SpecLessBenchAlgorithms Require Import BasicDomain Execution.

From SpecLessBenchAlgorithms.Generated Require Import FACTORIAL_V0.

Definition impl_FACTORIAL_V0 : implementation :=
  {| program := FACTORIAL_V0.prog; input_symbol := FACTORIAL_V0._eb_input; output_symbol := FACTORIAL_V0._eb_output |}.

From SpecLessBenchAlgorithms.Generated Require Import FACTORIAL_V1.

Definition impl_FACTORIAL_V1 : implementation :=
  {| program := FACTORIAL_V1.prog; input_symbol := FACTORIAL_V1._eb_input; output_symbol := FACTORIAL_V1._eb_output |}.

From SpecLessBenchAlgorithms.Generated Require Import FACTORIAL_V2.

Definition impl_FACTORIAL_V2 : implementation :=
  {| program := FACTORIAL_V2.prog; input_symbol := FACTORIAL_V2._eb_input; output_symbol := FACTORIAL_V2._eb_output |}.

Theorem R_FAC_EQ : Equivalent (BasicDomain.valid 0) BasicDomain.encode impl_FACTORIAL_V0 impl_FACTORIAL_V1.
Abort.

Theorem R_FAC_EQ_certificate : Certificate (BasicDomain.valid 0) BasicDomain.encode impl_FACTORIAL_V0 impl_FACTORIAL_V1.
Abort.

Theorem R_FAC_CEX : Counterexample (BasicDomain.valid 0) BasicDomain.encode impl_FACTORIAL_V0 impl_FACTORIAL_V2.
Abort.

Theorem R_FAC_CEX_certificate : Certificate (BasicDomain.valid 0) BasicDomain.encode impl_FACTORIAL_V0 impl_FACTORIAL_V2.
Abort.
