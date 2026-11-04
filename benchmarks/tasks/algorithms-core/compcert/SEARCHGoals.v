From EqualBenchAlgorithms Require Import BasicDomain Execution.

From EqualBenchAlgorithms.Generated Require Import SEARCH_V0.

Definition impl_SEARCH_V0 : implementation :=
  {| program := SEARCH_V0.prog; input_symbol := SEARCH_V0._eb_input; output_symbol := SEARCH_V0._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import SEARCH_V1.

Definition impl_SEARCH_V1 : implementation :=
  {| program := SEARCH_V1.prog; input_symbol := SEARCH_V1._eb_input; output_symbol := SEARCH_V1._eb_output |}.

From EqualBenchAlgorithms.Generated Require Import SEARCH_V2.

Definition impl_SEARCH_V2 : implementation :=
  {| program := SEARCH_V2.prog; input_symbol := SEARCH_V2._eb_input; output_symbol := SEARCH_V2._eb_output |}.

Theorem R_STR_EQ : Equivalent (BasicDomain.valid 4) BasicDomain.encode impl_SEARCH_V0 impl_SEARCH_V1.
Abort.

Theorem R_STR_EQ_certificate : Certificate (BasicDomain.valid 4) BasicDomain.encode impl_SEARCH_V0 impl_SEARCH_V1.
Abort.

Theorem R_STR_CEX : Counterexample (BasicDomain.valid 4) BasicDomain.encode impl_SEARCH_V0 impl_SEARCH_V2.
Abort.

Theorem R_STR_CEX_certificate : Certificate (BasicDomain.valid 4) BasicDomain.encode impl_SEARCH_V0 impl_SEARCH_V2.
Abort.
