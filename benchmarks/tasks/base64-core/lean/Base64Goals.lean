import Base64Domain
namespace SpecLessBenchBase64
def A_BASE64_STREAM_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def A_BASE64_STREAM_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def A_BASE64_PADDING_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def A_BASE64_PADDING_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
end SpecLessBenchBase64
