import Domain

import BasicDomain

namespace SpecLessBenchSubmission

def C_BST_SUCCESSOR_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.BST.valid (fun x => SpecLessBench.bst 0 (SpecLessBench.BST.encode x)) (fun x => SpecLessBench.bst 1 (SpecLessBench.BST.encode x))

def C_BST_SUCCESSOR_refutationAt (x : SpecLessBench.BST.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.BST.valid x ∧ (fun x => SpecLessBench.bst 0 (SpecLessBench.BST.encode x)) x = some oa ∧ (fun x => SpecLessBench.bst 1 (SpecLessBench.BST.encode x)) x = some ob ∧ oa ≠ ob

def C_BST_ROTATE_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.BST.valid (fun x => SpecLessBench.bst 0 (SpecLessBench.BST.encode x)) (fun x => SpecLessBench.bst 2 (SpecLessBench.BST.encode x))

def C_BST_ROTATE_refutationAt (x : SpecLessBench.BST.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.BST.valid x ∧ (fun x => SpecLessBench.bst 0 (SpecLessBench.BST.encode x)) x = some oa ∧ (fun x => SpecLessBench.bst 2 (SpecLessBench.BST.encode x)) x = some ob ∧ oa ≠ ob

def C_BST_VALUE_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.BST.valid (fun x => SpecLessBench.bst 0 (SpecLessBench.BST.encode x)) (fun x => SpecLessBench.bst 3 (SpecLessBench.BST.encode x))

def C_BST_VALUE_refutationAt (x : SpecLessBench.BST.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.BST.valid x ∧ (fun x => SpecLessBench.bst 0 (SpecLessBench.BST.encode x)) x = some oa ∧ (fun x => SpecLessBench.bst 3 (SpecLessBench.BST.encode x)) x = some ob ∧ oa ≠ ob

def C_AVL_STACK_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.AVL.valid (fun x => SpecLessBench.avl 0 (SpecLessBench.AVL.encode x)) (fun x => SpecLessBench.avl 1 (SpecLessBench.AVL.encode x))

def C_AVL_STACK_refutationAt (x : SpecLessBench.AVL.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.AVL.valid x ∧ (fun x => SpecLessBench.avl 0 (SpecLessBench.AVL.encode x)) x = some oa ∧ (fun x => SpecLessBench.avl 1 (SpecLessBench.AVL.encode x)) x = some ob ∧ oa ≠ ob

def C_AVL_FACTOR_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.AVL.valid (fun x => SpecLessBench.avl 0 (SpecLessBench.AVL.encode x)) (fun x => SpecLessBench.avl 2 (SpecLessBench.AVL.encode x))

def C_AVL_FACTOR_refutationAt (x : SpecLessBench.AVL.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.AVL.valid x ∧ (fun x => SpecLessBench.avl 0 (SpecLessBench.AVL.encode x)) x = some oa ∧ (fun x => SpecLessBench.avl 2 (SpecLessBench.AVL.encode x)) x = some ob ∧ oa ≠ ob

def C_AVL_MIDDLE_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.AVL.valid (fun x => SpecLessBench.avl 0 (SpecLessBench.AVL.encode x)) (fun x => SpecLessBench.avl 3 (SpecLessBench.AVL.encode x))

def C_AVL_MIDDLE_refutationAt (x : SpecLessBench.AVL.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.AVL.valid x ∧ (fun x => SpecLessBench.avl 0 (SpecLessBench.AVL.encode x)) x = some oa ∧ (fun x => SpecLessBench.avl 3 (SpecLessBench.AVL.encode x)) x = some ob ∧ oa ≠ ob

def C_RING_COPY_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.Ring.valid (fun x => SpecLessBench.ring 0 (SpecLessBench.Ring.encode x)) (fun x => SpecLessBench.ring 1 (SpecLessBench.Ring.encode x))

def C_RING_COPY_refutationAt (x : SpecLessBench.Ring.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.Ring.valid x ∧ (fun x => SpecLessBench.ring 0 (SpecLessBench.Ring.encode x)) x = some oa ∧ (fun x => SpecLessBench.ring 1 (SpecLessBench.Ring.encode x)) x = some ob ∧ oa ≠ ob

def C_RING_REP_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.Ring.valid (fun x => SpecLessBench.ring 0 (SpecLessBench.Ring.encode x)) (fun x => SpecLessBench.ring 2 (SpecLessBench.Ring.encode x))

def C_RING_REP_refutationAt (x : SpecLessBench.Ring.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.Ring.valid x ∧ (fun x => SpecLessBench.ring 0 (SpecLessBench.Ring.encode x)) x = some oa ∧ (fun x => SpecLessBench.ring 2 (SpecLessBench.Ring.encode x)) x = some ob ∧ oa ≠ ob

def C_RING_FULL_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.Ring.valid (fun x => SpecLessBench.ring 0 (SpecLessBench.Ring.encode x)) (fun x => SpecLessBench.ring 3 (SpecLessBench.Ring.encode x))

def C_RING_FULL_refutationAt (x : SpecLessBench.Ring.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.Ring.valid x ∧ (fun x => SpecLessBench.ring 0 (SpecLessBench.Ring.encode x)) x = some oa ∧ (fun x => SpecLessBench.ring 3 (SpecLessBench.Ring.encode x)) x = some ob ∧ oa ≠ ob

def C_DIJK_SCAN_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.Dijkstra.valid (fun x => SpecLessBench.dijkstra 0 (SpecLessBench.Dijkstra.encode x)) (fun x => SpecLessBench.dijkstra 1 (SpecLessBench.Dijkstra.encode x))

def C_DIJK_SCAN_refutationAt (x : SpecLessBench.Dijkstra.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.Dijkstra.valid x ∧ (fun x => SpecLessBench.dijkstra 0 (SpecLessBench.Dijkstra.encode x)) x = some oa ∧ (fun x => SpecLessBench.dijkstra 1 (SpecLessBench.Dijkstra.encode x)) x = some ob ∧ oa ≠ ob

def C_DIJK_HEAP_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.Dijkstra.valid (fun x => SpecLessBench.dijkstra 0 (SpecLessBench.Dijkstra.encode x)) (fun x => SpecLessBench.dijkstra 2 (SpecLessBench.Dijkstra.encode x))

def C_DIJK_HEAP_refutationAt (x : SpecLessBench.Dijkstra.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.Dijkstra.valid x ∧ (fun x => SpecLessBench.dijkstra 0 (SpecLessBench.Dijkstra.encode x)) x = some oa ∧ (fun x => SpecLessBench.dijkstra 2 (SpecLessBench.Dijkstra.encode x)) x = some ob ∧ oa ≠ ob

def C_DIJK_SEEN_equivalence : Prop := SpecLessBench.Equivalent SpecLessBench.Dijkstra.valid (fun x => SpecLessBench.dijkstra 0 (SpecLessBench.Dijkstra.encode x)) (fun x => SpecLessBench.dijkstra 3 (SpecLessBench.Dijkstra.encode x))

def C_DIJK_SEEN_refutationAt (x : SpecLessBench.Dijkstra.Input) (oa ob : List Int) : Prop :=
  SpecLessBench.Dijkstra.valid x ∧ (fun x => SpecLessBench.dijkstra 0 (SpecLessBench.Dijkstra.encode x)) x = some oa ∧ (fun x => SpecLessBench.dijkstra 3 (SpecLessBench.Dijkstra.encode x)) x = some ob ∧ oa ≠ ob

def R_FAC_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 1)

def R_FAC_EQ_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 0 x ∧ SpecLessBenchBasic.entry 0 0 x = some oa ∧ SpecLessBenchBasic.entry 0 1 x = some ob ∧ oa ≠ ob

def R_FAC_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 0) (SpecLessBenchBasic.entry 0 0) (SpecLessBenchBasic.entry 0 2)

def R_FAC_CEX_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 0 x ∧ SpecLessBenchBasic.entry 0 0 x = some oa ∧ SpecLessBenchBasic.entry 0 2 x = some ob ∧ oa ≠ ob

def R_REV_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 1) (SpecLessBenchBasic.entry 1 0) (SpecLessBenchBasic.entry 1 1)

def R_REV_EQ_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 1 x ∧ SpecLessBenchBasic.entry 1 0 x = some oa ∧ SpecLessBenchBasic.entry 1 1 x = some ob ∧ oa ≠ ob

def R_REV_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 1) (SpecLessBenchBasic.entry 1 0) (SpecLessBenchBasic.entry 1 2)

def R_REV_CEX_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 1 x ∧ SpecLessBenchBasic.entry 1 0 x = some oa ∧ SpecLessBenchBasic.entry 1 2 x = some ob ∧ oa ≠ ob

def R_SUM_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 2) (SpecLessBenchBasic.entry 2 0) (SpecLessBenchBasic.entry 2 1)

def R_SUM_EQ_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 2 x ∧ SpecLessBenchBasic.entry 2 0 x = some oa ∧ SpecLessBenchBasic.entry 2 1 x = some ob ∧ oa ≠ ob

def R_SUM_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 2) (SpecLessBenchBasic.entry 2 0) (SpecLessBenchBasic.entry 2 2)

def R_SUM_CEX_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 2 x ∧ SpecLessBenchBasic.entry 2 0 x = some oa ∧ SpecLessBenchBasic.entry 2 2 x = some ob ∧ oa ≠ ob

def R_MAT_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 3) (SpecLessBenchBasic.entry 3 0) (SpecLessBenchBasic.entry 3 1)

def R_MAT_EQ_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 3 x ∧ SpecLessBenchBasic.entry 3 0 x = some oa ∧ SpecLessBenchBasic.entry 3 1 x = some ob ∧ oa ≠ ob

def R_MAT_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 3) (SpecLessBenchBasic.entry 3 0) (SpecLessBenchBasic.entry 3 2)

def R_MAT_CEX_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 3 x ∧ SpecLessBenchBasic.entry 3 0 x = some oa ∧ SpecLessBenchBasic.entry 3 2 x = some ob ∧ oa ≠ ob

def R_STR_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 4) (SpecLessBenchBasic.entry 4 0) (SpecLessBenchBasic.entry 4 1)

def R_STR_EQ_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 4 x ∧ SpecLessBenchBasic.entry 4 0 x = some oa ∧ SpecLessBenchBasic.entry 4 1 x = some ob ∧ oa ≠ ob

def R_STR_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 4) (SpecLessBenchBasic.entry 4 0) (SpecLessBenchBasic.entry 4 2)

def R_STR_CEX_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 4 x ∧ SpecLessBenchBasic.entry 4 0 x = some oa ∧ SpecLessBenchBasic.entry 4 2 x = some ob ∧ oa ≠ ob

def R_QUE_EQ_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 5) (SpecLessBenchBasic.entry 5 0) (SpecLessBenchBasic.entry 5 1)

def R_QUE_EQ_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 5 x ∧ SpecLessBenchBasic.entry 5 0 x = some oa ∧ SpecLessBenchBasic.entry 5 1 x = some ob ∧ oa ≠ ob

def R_QUE_CEX_equivalence : Prop := SpecLessBenchBasic.Equivalent (SpecLessBenchBasic.valid 5) (SpecLessBenchBasic.entry 5 0) (SpecLessBenchBasic.entry 5 2)

def R_QUE_CEX_refutationAt (x oa ob : List Int) : Prop :=
  SpecLessBenchBasic.valid 5 x ∧ SpecLessBenchBasic.entry 5 0 x = some oa ∧ SpecLessBenchBasic.entry 5 2 x = some ob ∧ oa ≠ ob

end SpecLessBenchSubmission
