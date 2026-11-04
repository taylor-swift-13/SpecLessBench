From SpecLessBenchSystems Require Import SystemsDomain Execution.

From SpecLessBenchSystems.Generated Require Import GRAPH_V0.

Definition impl_GRAPH_V0 : implementation :=
 {| program := GRAPH_V0.prog; input_symbol := GRAPH_V0._eb_input; output_symbol := GRAPH_V0._eb_output |}.

From SpecLessBenchSystems.Generated Require Import GRAPH_V1.

Definition impl_GRAPH_V1 : implementation :=
 {| program := GRAPH_V1.prog; input_symbol := GRAPH_V1._eb_input; output_symbol := GRAPH_V1._eb_output |}.

From SpecLessBenchSystems.Generated Require Import GRAPH_V2.

Definition impl_GRAPH_V2 : implementation :=
 {| program := GRAPH_V2.prog; input_symbol := GRAPH_V2._eb_input; output_symbol := GRAPH_V2._eb_output |}.

Definition G_INVALIDATE_WORKLIST_equivalence : Prop := Equivalent (SystemsDomain.valid 0) SystemsDomain.encode impl_GRAPH_V0 impl_GRAPH_V1.

Definition G_INVALIDATE_WORKLIST_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 0) SystemsDomain.encode impl_GRAPH_V0 impl_GRAPH_V1 x oa ob.

Definition G_INVALIDATE_DIRTY_equivalence : Prop := Equivalent (SystemsDomain.valid 0) SystemsDomain.encode impl_GRAPH_V0 impl_GRAPH_V2.

Definition G_INVALIDATE_DIRTY_refutationAt (x : SystemsDomain.words) (oa ob : observation) : Prop := RefutationAt (SystemsDomain.valid 0) SystemsDomain.encode impl_GRAPH_V0 impl_GRAPH_V2 x oa ob.
