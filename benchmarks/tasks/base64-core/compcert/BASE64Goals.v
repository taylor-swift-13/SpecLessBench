From SpecLessBenchBase64 Require Import Base64Domain Execution.

From SpecLessBenchBase64.Generated Require Import BASE64_V0.

Definition impl_BASE64_V0 : implementation :=
 {| program := BASE64_V0.prog; input_symbol := BASE64_V0._eb_input; output_symbol := BASE64_V0._eb_output |}.

From SpecLessBenchBase64.Generated Require Import BASE64_V1.

Definition impl_BASE64_V1 : implementation :=
 {| program := BASE64_V1.prog; input_symbol := BASE64_V1._eb_input; output_symbol := BASE64_V1._eb_output |}.

From SpecLessBenchBase64.Generated Require Import BASE64_V2.

Definition impl_BASE64_V2 : implementation :=
 {| program := BASE64_V2.prog; input_symbol := BASE64_V2._eb_input; output_symbol := BASE64_V2._eb_output |}.

Definition A_BASE64_STREAM_equivalence : Prop := Equivalent (Base64Domain.valid 0) Base64Domain.encode impl_BASE64_V0 impl_BASE64_V1.

Definition A_BASE64_STREAM_refutationAt (x : Base64Domain.words) (oa ob : observation) : Prop := RefutationAt (Base64Domain.valid 0) Base64Domain.encode impl_BASE64_V0 impl_BASE64_V1 x oa ob.

Definition A_BASE64_PADDING_equivalence : Prop := Equivalent (Base64Domain.valid 0) Base64Domain.encode impl_BASE64_V0 impl_BASE64_V2.

Definition A_BASE64_PADDING_refutationAt (x : Base64Domain.words) (oa ob : observation) : Prop := RefutationAt (Base64Domain.valid 0) Base64Domain.encode impl_BASE64_V0 impl_BASE64_V2 x oa ob.
