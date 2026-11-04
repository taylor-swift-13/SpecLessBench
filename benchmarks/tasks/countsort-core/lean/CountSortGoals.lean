import CountSortDomain
namespace SpecLessBenchCountSort
def COUNT_01_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def COUNT_01_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def COUNT_02_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def COUNT_02_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
end SpecLessBenchCountSort
