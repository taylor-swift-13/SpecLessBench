import Domain

import BasicDomain

namespace EqualBenchSubmission

def C_BST_SUCCESSOR_equivalence : Prop := EqualBench.Equivalent EqualBench.BST.valid (fun x => EqualBench.bst 0 (EqualBench.BST.encode x)) (fun x => EqualBench.bst 1 (EqualBench.BST.encode x))

def C_BST_SUCCESSOR_refutationAt (x : EqualBench.BST.Input) (oa ob : List Int) : Prop :=
  EqualBench.BST.valid x ∧ (fun x => EqualBench.bst 0 (EqualBench.BST.encode x)) x = some oa ∧ (fun x => EqualBench.bst 1 (EqualBench.BST.encode x)) x = some ob ∧ oa ≠ ob

def C_BST_ROTATE_equivalence : Prop := EqualBench.Equivalent EqualBench.BST.valid (fun x => EqualBench.bst 0 (EqualBench.BST.encode x)) (fun x => EqualBench.bst 2 (EqualBench.BST.encode x))

def C_BST_ROTATE_refutationAt (x : EqualBench.BST.Input) (oa ob : List Int) : Prop :=
  EqualBench.BST.valid x ∧ (fun x => EqualBench.bst 0 (EqualBench.BST.encode x)) x = some oa ∧ (fun x => EqualBench.bst 2 (EqualBench.BST.encode x)) x = some ob ∧ oa ≠ ob

def C_BST_VALUE_equivalence : Prop := EqualBench.Equivalent EqualBench.BST.valid (fun x => EqualBench.bst 0 (EqualBench.BST.encode x)) (fun x => EqualBench.bst 3 (EqualBench.BST.encode x))

def C_BST_VALUE_refutationAt (x : EqualBench.BST.Input) (oa ob : List Int) : Prop :=
  EqualBench.BST.valid x ∧ (fun x => EqualBench.bst 0 (EqualBench.BST.encode x)) x = some oa ∧ (fun x => EqualBench.bst 3 (EqualBench.BST.encode x)) x = some ob ∧ oa ≠ ob

def C_AVL_STACK_equivalence : Prop := EqualBench.Equivalent EqualBench.AVL.valid (fun x => EqualBench.avl 0 (EqualBench.AVL.encode x)) (fun x => EqualBench.avl 1 (EqualBench.AVL.encode x))

def C_AVL_STACK_refutationAt (x : EqualBench.AVL.Input) (oa ob : List Int) : Prop :=
  EqualBench.AVL.valid x ∧ (fun x => EqualBench.avl 0 (EqualBench.AVL.encode x)) x = some oa ∧ (fun x => EqualBench.avl 1 (EqualBench.AVL.encode x)) x = some ob ∧ oa ≠ ob

def C_AVL_FACTOR_equivalence : Prop := EqualBench.Equivalent EqualBench.AVL.valid (fun x => EqualBench.avl 0 (EqualBench.AVL.encode x)) (fun x => EqualBench.avl 2 (EqualBench.AVL.encode x))

def C_AVL_FACTOR_refutationAt (x : EqualBench.AVL.Input) (oa ob : List Int) : Prop :=
  EqualBench.AVL.valid x ∧ (fun x => EqualBench.avl 0 (EqualBench.AVL.encode x)) x = some oa ∧ (fun x => EqualBench.avl 2 (EqualBench.AVL.encode x)) x = some ob ∧ oa ≠ ob

def C_AVL_MIDDLE_equivalence : Prop := EqualBench.Equivalent EqualBench.AVL.valid (fun x => EqualBench.avl 0 (EqualBench.AVL.encode x)) (fun x => EqualBench.avl 3 (EqualBench.AVL.encode x))

def C_AVL_MIDDLE_refutationAt (x : EqualBench.AVL.Input) (oa ob : List Int) : Prop :=
  EqualBench.AVL.valid x ∧ (fun x => EqualBench.avl 0 (EqualBench.AVL.encode x)) x = some oa ∧ (fun x => EqualBench.avl 3 (EqualBench.AVL.encode x)) x = some ob ∧ oa ≠ ob

def C_RING_COPY_equivalence : Prop := EqualBench.Equivalent EqualBench.Ring.valid (fun x => EqualBench.ring 0 (EqualBench.Ring.encode x)) (fun x => EqualBench.ring 1 (EqualBench.Ring.encode x))

def C_RING_COPY_refutationAt (x : EqualBench.Ring.Input) (oa ob : List Int) : Prop :=
  EqualBench.Ring.valid x ∧ (fun x => EqualBench.ring 0 (EqualBench.Ring.encode x)) x = some oa ∧ (fun x => EqualBench.ring 1 (EqualBench.Ring.encode x)) x = some ob ∧ oa ≠ ob

def C_RING_REP_equivalence : Prop := EqualBench.Equivalent EqualBench.Ring.valid (fun x => EqualBench.ring 0 (EqualBench.Ring.encode x)) (fun x => EqualBench.ring 2 (EqualBench.Ring.encode x))

def C_RING_REP_refutationAt (x : EqualBench.Ring.Input) (oa ob : List Int) : Prop :=
  EqualBench.Ring.valid x ∧ (fun x => EqualBench.ring 0 (EqualBench.Ring.encode x)) x = some oa ∧ (fun x => EqualBench.ring 2 (EqualBench.Ring.encode x)) x = some ob ∧ oa ≠ ob

def C_RING_FULL_equivalence : Prop := EqualBench.Equivalent EqualBench.Ring.valid (fun x => EqualBench.ring 0 (EqualBench.Ring.encode x)) (fun x => EqualBench.ring 3 (EqualBench.Ring.encode x))

def C_RING_FULL_refutationAt (x : EqualBench.Ring.Input) (oa ob : List Int) : Prop :=
  EqualBench.Ring.valid x ∧ (fun x => EqualBench.ring 0 (EqualBench.Ring.encode x)) x = some oa ∧ (fun x => EqualBench.ring 3 (EqualBench.Ring.encode x)) x = some ob ∧ oa ≠ ob

def C_DIJK_SCAN_equivalence : Prop := EqualBench.Equivalent EqualBench.Dijkstra.valid (fun x => EqualBench.dijkstra 0 (EqualBench.Dijkstra.encode x)) (fun x => EqualBench.dijkstra 1 (EqualBench.Dijkstra.encode x))

def C_DIJK_SCAN_refutationAt (x : EqualBench.Dijkstra.Input) (oa ob : List Int) : Prop :=
  EqualBench.Dijkstra.valid x ∧ (fun x => EqualBench.dijkstra 0 (EqualBench.Dijkstra.encode x)) x = some oa ∧ (fun x => EqualBench.dijkstra 1 (EqualBench.Dijkstra.encode x)) x = some ob ∧ oa ≠ ob

def C_DIJK_HEAP_equivalence : Prop := EqualBench.Equivalent EqualBench.Dijkstra.valid (fun x => EqualBench.dijkstra 0 (EqualBench.Dijkstra.encode x)) (fun x => EqualBench.dijkstra 2 (EqualBench.Dijkstra.encode x))

def C_DIJK_HEAP_refutationAt (x : EqualBench.Dijkstra.Input) (oa ob : List Int) : Prop :=
  EqualBench.Dijkstra.valid x ∧ (fun x => EqualBench.dijkstra 0 (EqualBench.Dijkstra.encode x)) x = some oa ∧ (fun x => EqualBench.dijkstra 2 (EqualBench.Dijkstra.encode x)) x = some ob ∧ oa ≠ ob

def C_DIJK_SEEN_equivalence : Prop := EqualBench.Equivalent EqualBench.Dijkstra.valid (fun x => EqualBench.dijkstra 0 (EqualBench.Dijkstra.encode x)) (fun x => EqualBench.dijkstra 3 (EqualBench.Dijkstra.encode x))

def C_DIJK_SEEN_refutationAt (x : EqualBench.Dijkstra.Input) (oa ob : List Int) : Prop :=
  EqualBench.Dijkstra.valid x ∧ (fun x => EqualBench.dijkstra 0 (EqualBench.Dijkstra.encode x)) x = some oa ∧ (fun x => EqualBench.dijkstra 3 (EqualBench.Dijkstra.encode x)) x = some ob ∧ oa ≠ ob

def R_FAC_EQ_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 0) (EqualBenchBasic.entry 0 0) (EqualBenchBasic.entry 0 1)

def R_FAC_EQ_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 0 x ∧ EqualBenchBasic.entry 0 0 x = some oa ∧ EqualBenchBasic.entry 0 1 x = some ob ∧ oa ≠ ob

def R_FAC_CEX_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 0) (EqualBenchBasic.entry 0 0) (EqualBenchBasic.entry 0 2)

def R_FAC_CEX_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 0 x ∧ EqualBenchBasic.entry 0 0 x = some oa ∧ EqualBenchBasic.entry 0 2 x = some ob ∧ oa ≠ ob

def R_REV_EQ_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 1) (EqualBenchBasic.entry 1 0) (EqualBenchBasic.entry 1 1)

def R_REV_EQ_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 1 x ∧ EqualBenchBasic.entry 1 0 x = some oa ∧ EqualBenchBasic.entry 1 1 x = some ob ∧ oa ≠ ob

def R_REV_CEX_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 1) (EqualBenchBasic.entry 1 0) (EqualBenchBasic.entry 1 2)

def R_REV_CEX_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 1 x ∧ EqualBenchBasic.entry 1 0 x = some oa ∧ EqualBenchBasic.entry 1 2 x = some ob ∧ oa ≠ ob

def R_SUM_EQ_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 2) (EqualBenchBasic.entry 2 0) (EqualBenchBasic.entry 2 1)

def R_SUM_EQ_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 2 x ∧ EqualBenchBasic.entry 2 0 x = some oa ∧ EqualBenchBasic.entry 2 1 x = some ob ∧ oa ≠ ob

def R_SUM_CEX_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 2) (EqualBenchBasic.entry 2 0) (EqualBenchBasic.entry 2 2)

def R_SUM_CEX_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 2 x ∧ EqualBenchBasic.entry 2 0 x = some oa ∧ EqualBenchBasic.entry 2 2 x = some ob ∧ oa ≠ ob

def R_MAT_EQ_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 3) (EqualBenchBasic.entry 3 0) (EqualBenchBasic.entry 3 1)

def R_MAT_EQ_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 3 x ∧ EqualBenchBasic.entry 3 0 x = some oa ∧ EqualBenchBasic.entry 3 1 x = some ob ∧ oa ≠ ob

def R_MAT_CEX_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 3) (EqualBenchBasic.entry 3 0) (EqualBenchBasic.entry 3 2)

def R_MAT_CEX_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 3 x ∧ EqualBenchBasic.entry 3 0 x = some oa ∧ EqualBenchBasic.entry 3 2 x = some ob ∧ oa ≠ ob

def R_STR_EQ_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 4) (EqualBenchBasic.entry 4 0) (EqualBenchBasic.entry 4 1)

def R_STR_EQ_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 4 x ∧ EqualBenchBasic.entry 4 0 x = some oa ∧ EqualBenchBasic.entry 4 1 x = some ob ∧ oa ≠ ob

def R_STR_CEX_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 4) (EqualBenchBasic.entry 4 0) (EqualBenchBasic.entry 4 2)

def R_STR_CEX_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 4 x ∧ EqualBenchBasic.entry 4 0 x = some oa ∧ EqualBenchBasic.entry 4 2 x = some ob ∧ oa ≠ ob

def R_QUE_EQ_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 5) (EqualBenchBasic.entry 5 0) (EqualBenchBasic.entry 5 1)

def R_QUE_EQ_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 5 x ∧ EqualBenchBasic.entry 5 0 x = some oa ∧ EqualBenchBasic.entry 5 1 x = some ob ∧ oa ≠ ob

def R_QUE_CEX_equivalence : Prop := EqualBenchBasic.Equivalent (EqualBenchBasic.valid 5) (EqualBenchBasic.entry 5 0) (EqualBenchBasic.entry 5 2)

def R_QUE_CEX_refutationAt (x oa ob : List Int) : Prop :=
  EqualBenchBasic.valid 5 x ∧ EqualBenchBasic.entry 5 0 x = some oa ∧ EqualBenchBasic.entry 5 2 x = some ob ∧ oa ≠ ob

end EqualBenchSubmission
