From EqualBenchClassics Require Import ClassicsDomain Execution.

From EqualBenchClassics.Generated Require Import FOREST_V0.

Definition impl_FOREST_V0 : implementation :=
 {| program := FOREST_V0.prog; input_symbol := FOREST_V0._eb_input; output_symbol := FOREST_V0._eb_output |}.

From EqualBenchClassics.Generated Require Import FOREST_V1.

Definition impl_FOREST_V1 : implementation :=
 {| program := FOREST_V1.prog; input_symbol := FOREST_V1._eb_input; output_symbol := FOREST_V1._eb_output |}.

From EqualBenchClassics.Generated Require Import FOREST_V2.

Definition impl_FOREST_V2 : implementation :=
 {| program := FOREST_V2.prog; input_symbol := FOREST_V2._eb_input; output_symbol := FOREST_V2._eb_output |}.

Definition MST_TIED_WEIGHT_equivalence : Prop := Equivalent (ClassicsDomain.valid 0) ClassicsDomain.encode impl_FOREST_V0 impl_FOREST_V1.

Definition MST_TIED_WEIGHT_refutationAt (x : ClassicsDomain.words) (oa ob : observation) : Prop := RefutationAt (ClassicsDomain.valid 0) ClassicsDomain.encode impl_FOREST_V0 impl_FOREST_V1 x oa ob.

Definition MST_UNIQUE_EDGES_equivalence : Prop := Equivalent (ClassicsDomain.valid 1) ClassicsDomain.encode impl_FOREST_V0 impl_FOREST_V1.

Definition MST_UNIQUE_EDGES_refutationAt (x : ClassicsDomain.words) (oa ob : observation) : Prop := RefutationAt (ClassicsDomain.valid 1) ClassicsDomain.encode impl_FOREST_V0 impl_FOREST_V1 x oa ob.

Definition MST_MAX_COUNTEREXAMPLE_equivalence : Prop := Equivalent (ClassicsDomain.valid 0) ClassicsDomain.encode impl_FOREST_V0 impl_FOREST_V2.

Definition MST_MAX_COUNTEREXAMPLE_refutationAt (x : ClassicsDomain.words) (oa ob : observation) : Prop := RefutationAt (ClassicsDomain.valid 0) ClassicsDomain.encode impl_FOREST_V0 impl_FOREST_V2 x oa ob.
