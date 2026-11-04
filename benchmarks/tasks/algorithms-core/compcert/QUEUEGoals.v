From SpecLessBenchAlgorithms Require Import BasicDomain Execution.

From SpecLessBenchAlgorithms.Generated Require Import QUEUE_V0.

Definition impl_QUEUE_V0 : implementation :=
  {| program := QUEUE_V0.prog; input_symbol := QUEUE_V0._eb_input; output_symbol := QUEUE_V0._eb_output |}.

From SpecLessBenchAlgorithms.Generated Require Import QUEUE_V1.

Definition impl_QUEUE_V1 : implementation :=
  {| program := QUEUE_V1.prog; input_symbol := QUEUE_V1._eb_input; output_symbol := QUEUE_V1._eb_output |}.

From SpecLessBenchAlgorithms.Generated Require Import QUEUE_V2.

Definition impl_QUEUE_V2 : implementation :=
  {| program := QUEUE_V2.prog; input_symbol := QUEUE_V2._eb_input; output_symbol := QUEUE_V2._eb_output |}.

Theorem R_QUE_EQ : Equivalent (BasicDomain.valid 5) BasicDomain.encode impl_QUEUE_V0 impl_QUEUE_V1.
Abort.

Theorem R_QUE_EQ_certificate : Certificate (BasicDomain.valid 5) BasicDomain.encode impl_QUEUE_V0 impl_QUEUE_V1.
Abort.

Theorem R_QUE_CEX : Counterexample (BasicDomain.valid 5) BasicDomain.encode impl_QUEUE_V0 impl_QUEUE_V2.
Abort.

Theorem R_QUE_CEX_certificate : Certificate (BasicDomain.valid 5) BasicDomain.encode impl_QUEUE_V0 impl_QUEUE_V2.
Abort.
