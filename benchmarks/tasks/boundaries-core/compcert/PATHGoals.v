From SpecLessBenchBoundary Require Import BoundaryDomain Execution.

From SpecLessBenchBoundary.Generated Require Import PATH_V0.

Definition impl_PATH_V0 : implementation :=
 {| program := PATH_V0.prog; input_symbol := PATH_V0._eb_input; output_symbol := PATH_V0._eb_output |}.

From SpecLessBenchBoundary.Generated Require Import PATH_V1.

Definition impl_PATH_V1 : implementation :=
 {| program := PATH_V1.prog; input_symbol := PATH_V1._eb_input; output_symbol := PATH_V1._eb_output |}.

From SpecLessBenchBoundary.Generated Require Import PATH_V2.

Definition impl_PATH_V2 : implementation :=
 {| program := PATH_V2.prog; input_symbol := PATH_V2._eb_input; output_symbol := PATH_V2._eb_output |}.

Definition B_PATH_REVERSE_equivalence : Prop := Equivalent (BoundaryDomain.valid 8) BoundaryDomain.encode impl_PATH_V0 impl_PATH_V1.

Definition B_PATH_REVERSE_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 8) BoundaryDomain.encode impl_PATH_V0 impl_PATH_V1 x oa ob.

Definition B_PATH_PARENTS_equivalence : Prop := Equivalent (BoundaryDomain.valid 8) BoundaryDomain.encode impl_PATH_V0 impl_PATH_V2.

Definition B_PATH_PARENTS_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 8) BoundaryDomain.encode impl_PATH_V0 impl_PATH_V2 x oa ob.
