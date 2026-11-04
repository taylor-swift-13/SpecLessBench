From SpecLessBenchBoundary Require Import BoundaryDomain Execution.

From SpecLessBenchBoundary.Generated Require Import TREE_V0.

Definition impl_TREE_V0 : implementation :=
 {| program := TREE_V0.prog; input_symbol := TREE_V0._eb_input; output_symbol := TREE_V0._eb_output |}.

From SpecLessBenchBoundary.Generated Require Import TREE_V1.

Definition impl_TREE_V1 : implementation :=
 {| program := TREE_V1.prog; input_symbol := TREE_V1._eb_input; output_symbol := TREE_V1._eb_output |}.

From SpecLessBenchBoundary.Generated Require Import TREE_V2.

Definition impl_TREE_V2 : implementation :=
 {| program := TREE_V2.prog; input_symbol := TREE_V2._eb_input; output_symbol := TREE_V2._eb_output |}.

Definition C_TREE_STACK_equivalence : Prop := Equivalent (BoundaryDomain.valid 0) BoundaryDomain.encode impl_TREE_V0 impl_TREE_V1.

Definition C_TREE_STACK_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 0) BoundaryDomain.encode impl_TREE_V0 impl_TREE_V1 x oa ob.

Definition C_TREE_SUBTREE_equivalence : Prop := Equivalent (BoundaryDomain.valid 0) BoundaryDomain.encode impl_TREE_V0 impl_TREE_V2.

Definition C_TREE_SUBTREE_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 0) BoundaryDomain.encode impl_TREE_V0 impl_TREE_V2 x oa ob.
