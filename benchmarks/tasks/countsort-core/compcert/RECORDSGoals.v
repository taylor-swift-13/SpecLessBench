From SpecLessBenchCountSort Require Import CountSortDomain Execution.

From SpecLessBenchCountSort.Generated Require Import RECORDS_V0.

Definition impl_RECORDS_V0 : implementation :=
 {| program := RECORDS_V0.prog; input_symbol := RECORDS_V0._eb_input; output_symbol := RECORDS_V0._eb_output |}.

From SpecLessBenchCountSort.Generated Require Import RECORDS_V1.

Definition impl_RECORDS_V1 : implementation :=
 {| program := RECORDS_V1.prog; input_symbol := RECORDS_V1._eb_input; output_symbol := RECORDS_V1._eb_output |}.

From SpecLessBenchCountSort.Generated Require Import RECORDS_V2.

Definition impl_RECORDS_V2 : implementation :=
 {| program := RECORDS_V2.prog; input_symbol := RECORDS_V2._eb_input; output_symbol := RECORDS_V2._eb_output |}.

Definition COUNT_01_equivalence : Prop := Equivalent (CountSortDomain.valid 0) CountSortDomain.encode impl_RECORDS_V0 impl_RECORDS_V1.

Definition COUNT_01_refutationAt (x : CountSortDomain.words) (oa ob : observation) : Prop := RefutationAt (CountSortDomain.valid 0) CountSortDomain.encode impl_RECORDS_V0 impl_RECORDS_V1 x oa ob.

Definition COUNT_02_equivalence : Prop := Equivalent (CountSortDomain.valid 0) CountSortDomain.encode impl_RECORDS_V0 impl_RECORDS_V2.

Definition COUNT_02_refutationAt (x : CountSortDomain.words) (oa ob : observation) : Prop := RefutationAt (CountSortDomain.valid 0) CountSortDomain.encode impl_RECORDS_V0 impl_RECORDS_V2 x oa ob.
