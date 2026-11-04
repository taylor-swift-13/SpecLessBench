From EqualBenchAlgorithms Require Import BasicDomain Execution.

From EqualBenchAlgorithms.Generated Require Import REVERSE_V0.

Definition impl_REVERSE_V0 : implementation :=
  {| program := REVERSE_V0.prog; input_symbol := REVERSE_V0._eb_input; output_symbol := REVERSE_V0._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import REVERSE_V1.

Definition impl_REVERSE_V1 : implementation :=
  {| program := REVERSE_V1.prog; input_symbol := REVERSE_V1._eb_input; output_symbol := REVERSE_V1._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import REVERSE_V2.

Definition impl_REVERSE_V2 : implementation :=
  {| program := REVERSE_V2.prog; input_symbol := REVERSE_V2._eb_input; output_symbol := REVERSE_V2._eb_output |}.

Theorem R_REV_EQ : Equivalent (BasicDomain.valid 1) BasicDomain.encode impl_REVERSE_V0 impl_REVERSE_V1.
Abort.

Theorem R_REV_EQ_certificate : Certificate (BasicDomain.valid 1) BasicDomain.encode impl_REVERSE_V0 impl_REVERSE_V1.
Abort.

Theorem R_REV_CEX : Counterexample (BasicDomain.valid 1) BasicDomain.encode impl_REVERSE_V0 impl_REVERSE_V2.
Abort.

Theorem R_REV_CEX_certificate : Certificate (BasicDomain.valid 1) BasicDomain.encode impl_REVERSE_V0 impl_REVERSE_V2.
Abort.
