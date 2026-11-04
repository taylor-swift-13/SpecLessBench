From SpecLessBenchStateful Require Import StatefulDomain Execution.

From SpecLessBenchStateful.Generated Require Import TRANSACTIONS_V0.

Definition impl_TRANSACTIONS_V0 : implementation :=
 {| program := TRANSACTIONS_V0.prog; input_symbol := TRANSACTIONS_V0._eb_input; output_symbol := TRANSACTIONS_V0._eb_output |}.

From SpecLessBenchStateful.Generated Require Import TRANSACTIONS_V1.

Definition impl_TRANSACTIONS_V1 : implementation :=
 {| program := TRANSACTIONS_V1.prog; input_symbol := TRANSACTIONS_V1._eb_input; output_symbol := TRANSACTIONS_V1._eb_output |}.

From SpecLessBenchStateful.Generated Require Import TRANSACTIONS_V2.

Definition impl_TRANSACTIONS_V2 : implementation :=
 {| program := TRANSACTIONS_V2.prog; input_symbol := TRANSACTIONS_V2._eb_input; output_symbol := TRANSACTIONS_V2._eb_output |}.

Definition S_TX_JOURNAL_equivalence : Prop := Equivalent (StatefulDomain.valid 1) StatefulDomain.encode impl_TRANSACTIONS_V0 impl_TRANSACTIONS_V1.

Definition S_TX_JOURNAL_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid 1) StatefulDomain.encode impl_TRANSACTIONS_V0 impl_TRANSACTIONS_V1 x oa ob.

Definition S_TX_COMMIT_equivalence : Prop := Equivalent (StatefulDomain.valid 1) StatefulDomain.encode impl_TRANSACTIONS_V0 impl_TRANSACTIONS_V2.

Definition S_TX_COMMIT_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid 1) StatefulDomain.encode impl_TRANSACTIONS_V0 impl_TRANSACTIONS_V2 x oa ob.
