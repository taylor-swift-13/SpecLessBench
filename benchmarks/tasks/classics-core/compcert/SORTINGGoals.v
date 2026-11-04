From SpecLessBenchClassics Require Import ClassicsDomain Execution.

From SpecLessBenchClassics.Generated Require Import SORTING_V0.

Definition impl_SORTING_V0 : implementation :=
 {| program := SORTING_V0.prog; input_symbol := SORTING_V0._eb_input; output_symbol := SORTING_V0._eb_output |}.

From SpecLessBenchClassics.Generated Require Import SORTING_V1.

Definition impl_SORTING_V1 : implementation :=
 {| program := SORTING_V1.prog; input_symbol := SORTING_V1._eb_input; output_symbol := SORTING_V1._eb_output |}.

From SpecLessBenchClassics.Generated Require Import SORTING_V2.

Definition impl_SORTING_V2 : implementation :=
 {| program := SORTING_V2.prog; input_symbol := SORTING_V2._eb_input; output_symbol := SORTING_V2._eb_output |}.

Definition SORT_MERGE_equivalence : Prop := Equivalent (ClassicsDomain.valid 2) ClassicsDomain.encode impl_SORTING_V0 impl_SORTING_V1.

Definition SORT_MERGE_refutationAt (x : ClassicsDomain.words) (oa ob : observation) : Prop := RefutationAt (ClassicsDomain.valid 2) ClassicsDomain.encode impl_SORTING_V0 impl_SORTING_V1 x oa ob.

Definition SORT_UNSTABLE_equivalence : Prop := Equivalent (ClassicsDomain.valid 2) ClassicsDomain.encode impl_SORTING_V0 impl_SORTING_V2.

Definition SORT_UNSTABLE_refutationAt (x : ClassicsDomain.words) (oa ob : observation) : Prop := RefutationAt (ClassicsDomain.valid 2) ClassicsDomain.encode impl_SORTING_V0 impl_SORTING_V2 x oa ob.
