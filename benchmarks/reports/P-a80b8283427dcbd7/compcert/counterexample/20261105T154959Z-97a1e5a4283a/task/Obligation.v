From Trusted Require Import BasicDomain Execution FACTORIAL_V0 FACTORIAL_V2.
Definition left_impl : implementation :=
  {| program := FACTORIAL_V0.prog; input_symbol := FACTORIAL_V0._eb_input; output_symbol := FACTORIAL_V0._eb_output |}.
Definition right_impl : implementation :=
  {| program := FACTORIAL_V2.prog; input_symbol := FACTORIAL_V2._eb_input; output_symbol := FACTORIAL_V2._eb_output |}.
Definition goal : Prop := Counterexample (BasicDomain.valid 0) BasicDomain.encode left_impl right_impl.
