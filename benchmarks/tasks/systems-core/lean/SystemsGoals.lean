import SystemsDomain
namespace SpecLessBenchSystems
def G_INVALIDATE_WORKLIST_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 1)
def G_INVALIDATE_WORKLIST_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 1) x oa ob
def G_INVALIDATE_DIRTY_equivalence : Prop := Equivalent (valid 0) (entry 0 0) (entry 0 2)
def G_INVALIDATE_DIRTY_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 0) (entry 0 0) (entry 0 2) x oa ob
def N_SCOPE_OVERLAY_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 1)
def N_SCOPE_OVERLAY_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 1) x oa ob
def N_SCOPE_TOMBSTONE_equivalence : Prop := Equivalent (valid 1) (entry 1 0) (entry 1 2)
def N_SCOPE_TOMBSTONE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 1) (entry 1 0) (entry 1 2) x oa ob
def T_LEASE_WHEEL_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 1)
def T_LEASE_WHEEL_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 1) x oa ob
def T_LEASE_STALE_equivalence : Prop := Equivalent (valid 2) (entry 2 0) (entry 2 2)
def T_LEASE_STALE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 2) (entry 2 0) (entry 2 2) x oa ob
def A_ALIGN_MINIMA_equivalence : Prop := Equivalent (valid 3) (entry 3 0) (entry 3 1)
def A_ALIGN_MINIMA_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 3) (entry 3 0) (entry 3 1) x oa ob
def A_ALIGN_TIES_equivalence : Prop := Equivalent (valid 3) (entry 3 0) (entry 3 2)
def A_ALIGN_TIES_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 3) (entry 3 0) (entry 3 2) x oa ob
def A_RESAMPLE_PHASE_equivalence : Prop := Equivalent (valid 4) (entry 4 0) (entry 4 1)
def A_RESAMPLE_PHASE_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 4) (entry 4 0) (entry 4 1) x oa ob
def A_RESAMPLE_HALF_equivalence : Prop := Equivalent (valid 4) (entry 4 0) (entry 4 2)
def A_RESAMPLE_HALF_refutationAt (x oa ob : Words) : Prop := RefutationAt (valid 4) (entry 4 0) (entry 4 2) x oa ob
end SpecLessBenchSystems
