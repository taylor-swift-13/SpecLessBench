From EqualBenchBoundary Require Import BoundaryDomain Execution.

From EqualBenchBoundary.Generated Require Import QUOTES_V0.

Definition impl_QUOTES_V0 : implementation :=
 {| program := QUOTES_V0.prog; input_symbol := QUOTES_V0._eb_input; output_symbol := QUOTES_V0._eb_output |}.

From EqualBenchBoundary.Generated Require Import QUOTES_V1.

Definition impl_QUOTES_V1 : implementation :=
 {| program := QUOTES_V1.prog; input_symbol := QUOTES_V1._eb_input; output_symbol := QUOTES_V1._eb_output |}.

From EqualBenchBoundary.Generated Require Import QUOTES_V2.

Definition impl_QUOTES_V2 : implementation :=
 {| program := QUOTES_V2.prog; input_symbol := QUOTES_V2._eb_input; output_symbol := QUOTES_V2._eb_output |}.

Definition B_QUOTE_SPANS_equivalence : Prop := Equivalent (BoundaryDomain.valid 6) BoundaryDomain.encode impl_QUOTES_V0 impl_QUOTES_V1.

Definition B_QUOTE_SPANS_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 6) BoundaryDomain.encode impl_QUOTES_V0 impl_QUOTES_V1 x oa ob.

Definition B_QUOTE_EMPTY_equivalence : Prop := Equivalent (BoundaryDomain.valid 6) BoundaryDomain.encode impl_QUOTES_V0 impl_QUOTES_V2.

Definition B_QUOTE_EMPTY_refutationAt (x : BoundaryDomain.words) (oa ob : observation) : Prop := RefutationAt (BoundaryDomain.valid 6) BoundaryDomain.encode impl_QUOTES_V0 impl_QUOTES_V2 x oa ob.
