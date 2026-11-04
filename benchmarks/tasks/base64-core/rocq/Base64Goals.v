From EqualBenchBase64Native Require Import Base64Native Base64Domain.

Definition A_BASE64_STREAM_equivalence : Prop := Base64Native.Equivalent (Base64Domain.valid 0) (Base64Native.entry 0 0) (Base64Native.entry 0 1).

Definition A_BASE64_STREAM_refutationAt (x oa ob : Base64Native.words) : Prop := Base64Native.RefutationAt (Base64Domain.valid 0) (Base64Native.entry 0 0) (Base64Native.entry 0 1) x oa ob.

Definition A_BASE64_PADDING_equivalence : Prop := Base64Native.Equivalent (Base64Domain.valid 0) (Base64Native.entry 0 0) (Base64Native.entry 0 2).

Definition A_BASE64_PADDING_refutationAt (x oa ob : Base64Native.words) : Prop := Base64Native.RefutationAt (Base64Domain.valid 0) (Base64Native.entry 0 0) (Base64Native.entry 0 2) x oa ob.
