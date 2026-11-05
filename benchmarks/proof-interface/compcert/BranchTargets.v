From Stdlib Require Import ZArith List.

From SpecLessBench.QCIP Require Import Domain Execution BSTBindings AVLBindings RINGBindings DIJKSTRABindings.

From SpecLessBenchAlgorithms Require Import BasicDomain Execution FACTORIALGoals REVERSEGoals SUMGoals MATRIXGoals SEARCHGoals QUEUEGoals.

Definition C_BST_SUCCESSOR_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.BST.valid SpecLessBench.QCIP.Domain.BST.encode SpecLessBench.QCIP.BSTBindings.impl_BST_V0 SpecLessBench.QCIP.BSTBindings.impl_BST_V1.

Definition C_BST_SUCCESSOR_refutationAt (x : SpecLessBench.QCIP.Domain.BST.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.BST.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.BSTBindings.impl_BST_V0 (SpecLessBench.QCIP.Domain.BST.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.BSTBindings.impl_BST_V1 (SpecLessBench.QCIP.Domain.BST.encode x) ob /\ oa <> ob.

Definition C_BST_ROTATE_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.BST.valid SpecLessBench.QCIP.Domain.BST.encode SpecLessBench.QCIP.BSTBindings.impl_BST_V0 SpecLessBench.QCIP.BSTBindings.impl_BST_V2.

Definition C_BST_ROTATE_refutationAt (x : SpecLessBench.QCIP.Domain.BST.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.BST.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.BSTBindings.impl_BST_V0 (SpecLessBench.QCIP.Domain.BST.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.BSTBindings.impl_BST_V2 (SpecLessBench.QCIP.Domain.BST.encode x) ob /\ oa <> ob.

Definition C_BST_VALUE_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.BST.valid SpecLessBench.QCIP.Domain.BST.encode SpecLessBench.QCIP.BSTBindings.impl_BST_V0 SpecLessBench.QCIP.BSTBindings.impl_BST_V3.

Definition C_BST_VALUE_refutationAt (x : SpecLessBench.QCIP.Domain.BST.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.BST.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.BSTBindings.impl_BST_V0 (SpecLessBench.QCIP.Domain.BST.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.BSTBindings.impl_BST_V3 (SpecLessBench.QCIP.Domain.BST.encode x) ob /\ oa <> ob.

Definition C_AVL_STACK_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.AVL.valid SpecLessBench.QCIP.Domain.AVL.encode SpecLessBench.QCIP.AVLBindings.impl_AVL_V0 SpecLessBench.QCIP.AVLBindings.impl_AVL_V1.

Definition C_AVL_STACK_refutationAt (x : SpecLessBench.QCIP.Domain.AVL.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.AVL.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.AVLBindings.impl_AVL_V0 (SpecLessBench.QCIP.Domain.AVL.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.AVLBindings.impl_AVL_V1 (SpecLessBench.QCIP.Domain.AVL.encode x) ob /\ oa <> ob.

Definition C_AVL_FACTOR_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.AVL.valid SpecLessBench.QCIP.Domain.AVL.encode SpecLessBench.QCIP.AVLBindings.impl_AVL_V0 SpecLessBench.QCIP.AVLBindings.impl_AVL_V2.

Definition C_AVL_FACTOR_refutationAt (x : SpecLessBench.QCIP.Domain.AVL.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.AVL.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.AVLBindings.impl_AVL_V0 (SpecLessBench.QCIP.Domain.AVL.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.AVLBindings.impl_AVL_V2 (SpecLessBench.QCIP.Domain.AVL.encode x) ob /\ oa <> ob.

Definition C_AVL_MIDDLE_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.AVL.valid SpecLessBench.QCIP.Domain.AVL.encode SpecLessBench.QCIP.AVLBindings.impl_AVL_V0 SpecLessBench.QCIP.AVLBindings.impl_AVL_V3.

Definition C_AVL_MIDDLE_refutationAt (x : SpecLessBench.QCIP.Domain.AVL.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.AVL.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.AVLBindings.impl_AVL_V0 (SpecLessBench.QCIP.Domain.AVL.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.AVLBindings.impl_AVL_V3 (SpecLessBench.QCIP.Domain.AVL.encode x) ob /\ oa <> ob.

Definition C_RING_COPY_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.Ring.valid SpecLessBench.QCIP.Domain.Ring.encode SpecLessBench.QCIP.RINGBindings.impl_RING_V0 SpecLessBench.QCIP.RINGBindings.impl_RING_V1.

Definition C_RING_COPY_refutationAt (x : SpecLessBench.QCIP.Domain.Ring.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.Ring.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.RINGBindings.impl_RING_V0 (SpecLessBench.QCIP.Domain.Ring.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.RINGBindings.impl_RING_V1 (SpecLessBench.QCIP.Domain.Ring.encode x) ob /\ oa <> ob.

Definition C_RING_REP_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.Ring.valid SpecLessBench.QCIP.Domain.Ring.encode SpecLessBench.QCIP.RINGBindings.impl_RING_V0 SpecLessBench.QCIP.RINGBindings.impl_RING_V2.

Definition C_RING_REP_refutationAt (x : SpecLessBench.QCIP.Domain.Ring.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.Ring.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.RINGBindings.impl_RING_V0 (SpecLessBench.QCIP.Domain.Ring.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.RINGBindings.impl_RING_V2 (SpecLessBench.QCIP.Domain.Ring.encode x) ob /\ oa <> ob.

Definition C_RING_FULL_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.Ring.valid SpecLessBench.QCIP.Domain.Ring.encode SpecLessBench.QCIP.RINGBindings.impl_RING_V0 SpecLessBench.QCIP.RINGBindings.impl_RING_V3.

Definition C_RING_FULL_refutationAt (x : SpecLessBench.QCIP.Domain.Ring.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.Ring.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.RINGBindings.impl_RING_V0 (SpecLessBench.QCIP.Domain.Ring.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.RINGBindings.impl_RING_V3 (SpecLessBench.QCIP.Domain.Ring.encode x) ob /\ oa <> ob.

Definition C_DIJK_SCAN_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.Dijkstra.valid SpecLessBench.QCIP.Domain.Dijkstra.encode SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V1.

Definition C_DIJK_SCAN_refutationAt (x : SpecLessBench.QCIP.Domain.Dijkstra.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.Dijkstra.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 (SpecLessBench.QCIP.Domain.Dijkstra.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V1 (SpecLessBench.QCIP.Domain.Dijkstra.encode x) ob /\ oa <> ob.

Definition C_DIJK_HEAP_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.Dijkstra.valid SpecLessBench.QCIP.Domain.Dijkstra.encode SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V2.

Definition C_DIJK_HEAP_refutationAt (x : SpecLessBench.QCIP.Domain.Dijkstra.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.Dijkstra.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 (SpecLessBench.QCIP.Domain.Dijkstra.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V2 (SpecLessBench.QCIP.Domain.Dijkstra.encode x) ob /\ oa <> ob.

Definition C_DIJK_SEEN_equivalence : Prop := SpecLessBench.QCIP.Execution.Equivalent SpecLessBench.QCIP.Domain.Dijkstra.valid SpecLessBench.QCIP.Domain.Dijkstra.encode SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V3.

Definition C_DIJK_SEEN_refutationAt (x : SpecLessBench.QCIP.Domain.Dijkstra.input) (oa ob : SpecLessBench.QCIP.Execution.observation) : Prop :=
  SpecLessBench.QCIP.Domain.Dijkstra.valid x /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 (SpecLessBench.QCIP.Domain.Dijkstra.encode x) oa /\ SpecLessBench.QCIP.Execution.run SpecLessBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V3 (SpecLessBench.QCIP.Domain.Dijkstra.encode x) ob /\ oa <> ob.

Definition R_FAC_EQ_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 0) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V1.

Definition R_FAC_EQ_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 0 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V1 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_FAC_CEX_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 0) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V2.

Definition R_FAC_CEX_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 0 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V2 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_REV_EQ_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 1) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V1.

Definition R_REV_EQ_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 1 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V1 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_REV_CEX_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 1) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V2.

Definition R_REV_CEX_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 1 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.REVERSEGoals.impl_REVERSE_V2 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_SUM_EQ_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 2) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V0 SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V1.

Definition R_SUM_EQ_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 2 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V1 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_SUM_CEX_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 2) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V0 SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V2.

Definition R_SUM_CEX_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 2 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SUMGoals.impl_SUM_V2 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_MAT_EQ_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 3) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V1.

Definition R_MAT_EQ_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 3 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V1 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_MAT_CEX_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 3) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V2.

Definition R_MAT_CEX_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 3 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.MATRIXGoals.impl_MATRIX_V2 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_STR_EQ_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 4) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V1.

Definition R_STR_EQ_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 4 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V1 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_STR_CEX_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 4) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V2.

Definition R_STR_CEX_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 4 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.SEARCHGoals.impl_SEARCH_V2 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_QUE_EQ_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 5) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V1.

Definition R_QUE_EQ_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 5 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V1 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_QUE_CEX_equivalence : Prop := SpecLessBenchAlgorithms.Execution.Equivalent (SpecLessBenchAlgorithms.BasicDomain.valid 5) SpecLessBenchAlgorithms.BasicDomain.encode SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V2.

Definition R_QUE_CEX_refutationAt (x : list Z) (oa ob : SpecLessBenchAlgorithms.Execution.observation) : Prop :=
  SpecLessBenchAlgorithms.BasicDomain.valid 5 x /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 (SpecLessBenchAlgorithms.BasicDomain.encode x) oa /\ SpecLessBenchAlgorithms.Execution.run SpecLessBenchAlgorithms.QUEUEGoals.impl_QUEUE_V2 (SpecLessBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.
