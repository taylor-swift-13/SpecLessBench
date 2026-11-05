From Coq Require Import ZArith List.

From SpecLessBench.QCIP Require Import Domain.

From SpecLessBenchNative Require Import Native.

From SpecLessBenchBasic Require Import BasicNative BasicDomain.

Definition C_BST_SUCCESSOR_equivalence : Prop := Native.Equivalent Domain.BST.valid (fun x => Native.bst 0 (Domain.BST.encode x)) (fun x => Native.bst 1 (Domain.BST.encode x)).

Definition C_BST_SUCCESSOR_refutationAt (x : Domain.BST.input) (oa ob : list Z) : Prop :=
  Domain.BST.valid x /\ (fun x => Native.bst 0 (Domain.BST.encode x)) x = Some oa /\ (fun x => Native.bst 1 (Domain.BST.encode x)) x = Some ob /\ oa <> ob.

Definition C_BST_ROTATE_equivalence : Prop := Native.Equivalent Domain.BST.valid (fun x => Native.bst 0 (Domain.BST.encode x)) (fun x => Native.bst 2 (Domain.BST.encode x)).

Definition C_BST_ROTATE_refutationAt (x : Domain.BST.input) (oa ob : list Z) : Prop :=
  Domain.BST.valid x /\ (fun x => Native.bst 0 (Domain.BST.encode x)) x = Some oa /\ (fun x => Native.bst 2 (Domain.BST.encode x)) x = Some ob /\ oa <> ob.

Definition C_BST_VALUE_equivalence : Prop := Native.Equivalent Domain.BST.valid (fun x => Native.bst 0 (Domain.BST.encode x)) (fun x => Native.bst 3 (Domain.BST.encode x)).

Definition C_BST_VALUE_refutationAt (x : Domain.BST.input) (oa ob : list Z) : Prop :=
  Domain.BST.valid x /\ (fun x => Native.bst 0 (Domain.BST.encode x)) x = Some oa /\ (fun x => Native.bst 3 (Domain.BST.encode x)) x = Some ob /\ oa <> ob.

Definition C_AVL_STACK_equivalence : Prop := Native.Equivalent Domain.AVL.valid (fun x => Native.avl 0 (Domain.AVL.encode x)) (fun x => Native.avl 1 (Domain.AVL.encode x)).

Definition C_AVL_STACK_refutationAt (x : Domain.AVL.input) (oa ob : list Z) : Prop :=
  Domain.AVL.valid x /\ (fun x => Native.avl 0 (Domain.AVL.encode x)) x = Some oa /\ (fun x => Native.avl 1 (Domain.AVL.encode x)) x = Some ob /\ oa <> ob.

Definition C_AVL_FACTOR_equivalence : Prop := Native.Equivalent Domain.AVL.valid (fun x => Native.avl 0 (Domain.AVL.encode x)) (fun x => Native.avl 2 (Domain.AVL.encode x)).

Definition C_AVL_FACTOR_refutationAt (x : Domain.AVL.input) (oa ob : list Z) : Prop :=
  Domain.AVL.valid x /\ (fun x => Native.avl 0 (Domain.AVL.encode x)) x = Some oa /\ (fun x => Native.avl 2 (Domain.AVL.encode x)) x = Some ob /\ oa <> ob.

Definition C_AVL_MIDDLE_equivalence : Prop := Native.Equivalent Domain.AVL.valid (fun x => Native.avl 0 (Domain.AVL.encode x)) (fun x => Native.avl 3 (Domain.AVL.encode x)).

Definition C_AVL_MIDDLE_refutationAt (x : Domain.AVL.input) (oa ob : list Z) : Prop :=
  Domain.AVL.valid x /\ (fun x => Native.avl 0 (Domain.AVL.encode x)) x = Some oa /\ (fun x => Native.avl 3 (Domain.AVL.encode x)) x = Some ob /\ oa <> ob.

Definition C_RING_COPY_equivalence : Prop := Native.Equivalent Domain.Ring.valid (fun x => Native.ring 0 (Domain.Ring.encode x)) (fun x => Native.ring 1 (Domain.Ring.encode x)).

Definition C_RING_COPY_refutationAt (x : Domain.Ring.input) (oa ob : list Z) : Prop :=
  Domain.Ring.valid x /\ (fun x => Native.ring 0 (Domain.Ring.encode x)) x = Some oa /\ (fun x => Native.ring 1 (Domain.Ring.encode x)) x = Some ob /\ oa <> ob.

Definition C_RING_REP_equivalence : Prop := Native.Equivalent Domain.Ring.valid (fun x => Native.ring 0 (Domain.Ring.encode x)) (fun x => Native.ring 2 (Domain.Ring.encode x)).

Definition C_RING_REP_refutationAt (x : Domain.Ring.input) (oa ob : list Z) : Prop :=
  Domain.Ring.valid x /\ (fun x => Native.ring 0 (Domain.Ring.encode x)) x = Some oa /\ (fun x => Native.ring 2 (Domain.Ring.encode x)) x = Some ob /\ oa <> ob.

Definition C_RING_FULL_equivalence : Prop := Native.Equivalent Domain.Ring.valid (fun x => Native.ring 0 (Domain.Ring.encode x)) (fun x => Native.ring 3 (Domain.Ring.encode x)).

Definition C_RING_FULL_refutationAt (x : Domain.Ring.input) (oa ob : list Z) : Prop :=
  Domain.Ring.valid x /\ (fun x => Native.ring 0 (Domain.Ring.encode x)) x = Some oa /\ (fun x => Native.ring 3 (Domain.Ring.encode x)) x = Some ob /\ oa <> ob.

Definition C_DIJK_SCAN_equivalence : Prop := Native.Equivalent Domain.Dijkstra.valid (fun x => Native.dijkstra 0 (Domain.Dijkstra.encode x)) (fun x => Native.dijkstra 1 (Domain.Dijkstra.encode x)).

Definition C_DIJK_SCAN_refutationAt (x : Domain.Dijkstra.input) (oa ob : list Z) : Prop :=
  Domain.Dijkstra.valid x /\ (fun x => Native.dijkstra 0 (Domain.Dijkstra.encode x)) x = Some oa /\ (fun x => Native.dijkstra 1 (Domain.Dijkstra.encode x)) x = Some ob /\ oa <> ob.

Definition C_DIJK_HEAP_equivalence : Prop := Native.Equivalent Domain.Dijkstra.valid (fun x => Native.dijkstra 0 (Domain.Dijkstra.encode x)) (fun x => Native.dijkstra 2 (Domain.Dijkstra.encode x)).

Definition C_DIJK_HEAP_refutationAt (x : Domain.Dijkstra.input) (oa ob : list Z) : Prop :=
  Domain.Dijkstra.valid x /\ (fun x => Native.dijkstra 0 (Domain.Dijkstra.encode x)) x = Some oa /\ (fun x => Native.dijkstra 2 (Domain.Dijkstra.encode x)) x = Some ob /\ oa <> ob.

Definition C_DIJK_SEEN_equivalence : Prop := Native.Equivalent Domain.Dijkstra.valid (fun x => Native.dijkstra 0 (Domain.Dijkstra.encode x)) (fun x => Native.dijkstra 3 (Domain.Dijkstra.encode x)).

Definition C_DIJK_SEEN_refutationAt (x : Domain.Dijkstra.input) (oa ob : list Z) : Prop :=
  Domain.Dijkstra.valid x /\ (fun x => Native.dijkstra 0 (Domain.Dijkstra.encode x)) x = Some oa /\ (fun x => Native.dijkstra 3 (Domain.Dijkstra.encode x)) x = Some ob /\ oa <> ob.

Definition R_FAC_EQ_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 1).

Definition R_FAC_EQ_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 0 x /\ BasicNative.entry 0 0 x = Some oa /\ BasicNative.entry 0 1 x = Some ob /\ oa <> ob.

Definition R_FAC_CEX_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 2).

Definition R_FAC_CEX_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 0 x /\ BasicNative.entry 0 0 x = Some oa /\ BasicNative.entry 0 2 x = Some ob /\ oa <> ob.

Definition R_REV_EQ_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 1) (BasicNative.entry 1 0) (BasicNative.entry 1 1).

Definition R_REV_EQ_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 1 x /\ BasicNative.entry 1 0 x = Some oa /\ BasicNative.entry 1 1 x = Some ob /\ oa <> ob.

Definition R_REV_CEX_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 1) (BasicNative.entry 1 0) (BasicNative.entry 1 2).

Definition R_REV_CEX_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 1 x /\ BasicNative.entry 1 0 x = Some oa /\ BasicNative.entry 1 2 x = Some ob /\ oa <> ob.

Definition R_SUM_EQ_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 2) (BasicNative.entry 2 0) (BasicNative.entry 2 1).

Definition R_SUM_EQ_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 2 x /\ BasicNative.entry 2 0 x = Some oa /\ BasicNative.entry 2 1 x = Some ob /\ oa <> ob.

Definition R_SUM_CEX_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 2) (BasicNative.entry 2 0) (BasicNative.entry 2 2).

Definition R_SUM_CEX_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 2 x /\ BasicNative.entry 2 0 x = Some oa /\ BasicNative.entry 2 2 x = Some ob /\ oa <> ob.

Definition R_MAT_EQ_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 3) (BasicNative.entry 3 0) (BasicNative.entry 3 1).

Definition R_MAT_EQ_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 3 x /\ BasicNative.entry 3 0 x = Some oa /\ BasicNative.entry 3 1 x = Some ob /\ oa <> ob.

Definition R_MAT_CEX_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 3) (BasicNative.entry 3 0) (BasicNative.entry 3 2).

Definition R_MAT_CEX_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 3 x /\ BasicNative.entry 3 0 x = Some oa /\ BasicNative.entry 3 2 x = Some ob /\ oa <> ob.

Definition R_STR_EQ_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 4) (BasicNative.entry 4 0) (BasicNative.entry 4 1).

Definition R_STR_EQ_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 4 x /\ BasicNative.entry 4 0 x = Some oa /\ BasicNative.entry 4 1 x = Some ob /\ oa <> ob.

Definition R_STR_CEX_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 4) (BasicNative.entry 4 0) (BasicNative.entry 4 2).

Definition R_STR_CEX_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 4 x /\ BasicNative.entry 4 0 x = Some oa /\ BasicNative.entry 4 2 x = Some ob /\ oa <> ob.

Definition R_QUE_EQ_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 5) (BasicNative.entry 5 0) (BasicNative.entry 5 1).

Definition R_QUE_EQ_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 5 x /\ BasicNative.entry 5 0 x = Some oa /\ BasicNative.entry 5 1 x = Some ob /\ oa <> ob.

Definition R_QUE_CEX_equivalence : Prop := BasicNative.Equivalent (BasicDomain.valid 5) (BasicNative.entry 5 0) (BasicNative.entry 5 2).

Definition R_QUE_CEX_refutationAt (x oa ob : list Z) : Prop :=
  BasicDomain.valid 5 x /\ BasicNative.entry 5 0 x = Some oa /\ BasicNative.entry 5 2 x = Some ob /\ oa <> ob.
