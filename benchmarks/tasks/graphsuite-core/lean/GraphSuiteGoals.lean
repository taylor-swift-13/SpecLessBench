import GraphSuiteDomain
namespace SpecLessBenchGraphSuite
def APSP_01_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def APSP_01_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def APSP_02_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def APSP_02_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
def SCC_01_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 1)
def SCC_01_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 1) x oa ob
def SCC_02_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 2)
def SCC_02_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 2) x oa ob
def BM_01_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 1)
def BM_01_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 1) x oa ob
def BM_02_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 2)
def BM_02_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 2) x oa ob
end SpecLessBenchGraphSuite
