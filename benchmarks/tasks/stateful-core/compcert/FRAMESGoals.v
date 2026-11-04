From SpecLessBenchStateful Require Import StatefulDomain Execution.

From SpecLessBenchStateful.Generated Require Import FRAMES_V0.

Definition impl_FRAMES_V0 : implementation :=
 {| program := FRAMES_V0.prog; input_symbol := FRAMES_V0._eb_input; output_symbol := FRAMES_V0._eb_output |}.

From SpecLessBenchStateful.Generated Require Import FRAMES_V1.

Definition impl_FRAMES_V1 : implementation :=
 {| program := FRAMES_V1.prog; input_symbol := FRAMES_V1._eb_input; output_symbol := FRAMES_V1._eb_output |}.

From SpecLessBenchStateful.Generated Require Import FRAMES_V2.

Definition impl_FRAMES_V2 : implementation :=
 {| program := FRAMES_V2.prog; input_symbol := FRAMES_V2._eb_input; output_symbol := FRAMES_V2._eb_output |}.

Definition S_FRAME_RING_equivalence : Prop := Equivalent (StatefulDomain.valid 0) StatefulDomain.encode impl_FRAMES_V0 impl_FRAMES_V1.

Definition S_FRAME_RING_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid 0) StatefulDomain.encode impl_FRAMES_V0 impl_FRAMES_V1 x oa ob.

Definition S_FRAME_EMPTY_equivalence : Prop := Equivalent (StatefulDomain.valid 0) StatefulDomain.encode impl_FRAMES_V0 impl_FRAMES_V2.

Definition S_FRAME_EMPTY_refutationAt (x : StatefulDomain.words) (oa ob : observation) : Prop := RefutationAt (StatefulDomain.valid 0) StatefulDomain.encode impl_FRAMES_V0 impl_FRAMES_V2 x oa ob.
