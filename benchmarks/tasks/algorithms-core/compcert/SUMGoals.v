From EqualBenchAlgorithms Require Import BasicDomain Execution.

From EqualBenchAlgorithms.Generated Require Import SUM_V0.

Definition impl_SUM_V0 : implementation :=
  {| program := SUM_V0.prog; input_symbol := SUM_V0._eb_input; output_symbol := SUM_V0._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import SUM_V1.

Definition impl_SUM_V1 : implementation :=
  {| program := SUM_V1.prog; input_symbol := SUM_V1._eb_input; output_symbol := SUM_V1._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import SUM_V2.

Definition impl_SUM_V2 : implementation :=
  {| program := SUM_V2.prog; input_symbol := SUM_V2._eb_input; output_symbol := SUM_V2._eb_output |}.

Theorem R_SUM_EQ : Equivalent (BasicDomain.valid 2) BasicDomain.encode impl_SUM_V0 impl_SUM_V1.
Abort.

Theorem R_SUM_EQ_certificate : Certificate (BasicDomain.valid 2) BasicDomain.encode impl_SUM_V0 impl_SUM_V1.
Abort.

Theorem R_SUM_CEX : Counterexample (BasicDomain.valid 2) BasicDomain.encode impl_SUM_V0 impl_SUM_V2.
Abort.

Theorem R_SUM_CEX_certificate : Certificate (BasicDomain.valid 2) BasicDomain.encode impl_SUM_V0 impl_SUM_V2.
Abort.
