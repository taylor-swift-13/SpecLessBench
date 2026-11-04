From EqualBenchAlgorithms Require Import BasicDomain Execution.

From EqualBenchAlgorithms.Generated Require Import MATRIX_V0.

Definition impl_MATRIX_V0 : implementation :=
  {| program := MATRIX_V0.prog; input_symbol := MATRIX_V0._eb_input; output_symbol := MATRIX_V0._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import MATRIX_V1.

Definition impl_MATRIX_V1 : implementation :=
  {| program := MATRIX_V1.prog; input_symbol := MATRIX_V1._eb_input; output_symbol := MATRIX_V1._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import MATRIX_V2.

Definition impl_MATRIX_V2 : implementation :=
  {| program := MATRIX_V2.prog; input_symbol := MATRIX_V2._eb_input; output_symbol := MATRIX_V2._eb_output |}.

Theorem R_MAT_EQ : Equivalent (BasicDomain.valid 3) BasicDomain.encode impl_MATRIX_V0 impl_MATRIX_V1.
Abort.

Theorem R_MAT_EQ_certificate : Certificate (BasicDomain.valid 3) BasicDomain.encode impl_MATRIX_V0 impl_MATRIX_V1.
Abort.

Theorem R_MAT_CEX : Counterexample (BasicDomain.valid 3) BasicDomain.encode impl_MATRIX_V0 impl_MATRIX_V2.
Abort.

Theorem R_MAT_CEX_certificate : Certificate (BasicDomain.valid 3) BasicDomain.encode impl_MATRIX_V0 impl_MATRIX_V2.
Abort.
