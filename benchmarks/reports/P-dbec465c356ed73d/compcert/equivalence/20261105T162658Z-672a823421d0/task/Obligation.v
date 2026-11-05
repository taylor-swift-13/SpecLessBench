From Trusted Require Import BasicDomain Execution FACTORIAL_V0 FACTORIAL_V1.
Definition left_impl : implementation :=
  {| program := FACTORIAL_V0.prog; input_symbol := FACTORIAL_V0._eb_input; output_symbol := FACTORIAL_V0._eb_output |}.
Definition right_impl : implementation :=
  {| program := FACTORIAL_V1.prog; input_symbol := FACTORIAL_V1._eb_input; output_symbol := FACTORIAL_V1._eb_output |}.
Definition goal : Prop := Equivalent (BasicDomain.valid 0) BasicDomain.encode left_impl right_impl.
