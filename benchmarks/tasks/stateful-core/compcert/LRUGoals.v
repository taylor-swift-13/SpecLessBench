From EqualBenchStateful Require Import StatefulDomain Execution.

From EqualBenchStateful.Generated Require Import LRU_V0.

Definition impl_LRU_V0 : implementation :=
 {| program := LRU_V0.prog; input_symbol := LRU_V0._eb_input; output_symbol := LRU_V0._eb_output |}.

From EqualBenchStateful.Generated Require Import LRU_V1.

Definition impl_LRU_V1 : implementation :=
 {| program := LRU_V1.prog; input_symbol := LRU_V1._eb_input; output_symbol := LRU_V1._eb_output |}.

From EqualBenchStateful.Generated Require Import LRU_V2.

Definition impl_LRU_V2 : implementation :=
 {| program := LRU_V2.prog; input_symbol := LRU_V2._eb_input; output_symbol := LRU_V2._eb_output |}.

Definition S_LRU_LINKS_equivalence : Prop := Equivalent (StatefulDomain.valid 2) StatefulDomain.encode impl_LRU_V0 impl_LRU_V1.

Definition S_LRU_LINKS_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid 2) StatefulDomain.encode impl_LRU_V0 impl_LRU_V1 x oa ob.

Definition S_LRU_TOUCH_equivalence : Prop := Equivalent (StatefulDomain.valid 2) StatefulDomain.encode impl_LRU_V0 impl_LRU_V2.

Definition S_LRU_TOUCH_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid 2) StatefulDomain.encode impl_LRU_V0 impl_LRU_V2 x oa ob.
