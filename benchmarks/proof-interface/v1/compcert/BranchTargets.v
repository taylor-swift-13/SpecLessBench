From Stdlib Require Import ZArith List.

From EqualBench.QCIP Require Import Domain Execution BSTBindings AVLBindings RINGBindings DIJKSTRABindings.

From EqualBenchAlgorithms Require Import BasicDomain Execution FACTORIALGoals REVERSEGoals SUMGoals MATRIXGoals SEARCHGoals QUEUEGoals.

Definition C_BST_SUCCESSOR_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.BST.valid EqualBench.QCIP.Domain.BST.encode EqualBench.QCIP.BSTBindings.impl_BST_V0 EqualBench.QCIP.BSTBindings.impl_BST_V1.

Definition C_BST_SUCCESSOR_refutationAt (x : EqualBench.QCIP.Domain.BST.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.BST.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.BSTBindings.impl_BST_V0 (EqualBench.QCIP.Domain.BST.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.BSTBindings.impl_BST_V1 (EqualBench.QCIP.Domain.BST.encode x) ob /\ oa <> ob.

Definition C_BST_ROTATE_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.BST.valid EqualBench.QCIP.Domain.BST.encode EqualBench.QCIP.BSTBindings.impl_BST_V0 EqualBench.QCIP.BSTBindings.impl_BST_V2.

Definition C_BST_ROTATE_refutationAt (x : EqualBench.QCIP.Domain.BST.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.BST.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.BSTBindings.impl_BST_V0 (EqualBench.QCIP.Domain.BST.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.BSTBindings.impl_BST_V2 (EqualBench.QCIP.Domain.BST.encode x) ob /\ oa <> ob.

Definition C_BST_VALUE_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.BST.valid EqualBench.QCIP.Domain.BST.encode EqualBench.QCIP.BSTBindings.impl_BST_V0 EqualBench.QCIP.BSTBindings.impl_BST_V3.

Definition C_BST_VALUE_refutationAt (x : EqualBench.QCIP.Domain.BST.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.BST.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.BSTBindings.impl_BST_V0 (EqualBench.QCIP.Domain.BST.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.BSTBindings.impl_BST_V3 (EqualBench.QCIP.Domain.BST.encode x) ob /\ oa <> ob.

Definition C_AVL_STACK_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.AVL.valid EqualBench.QCIP.Domain.AVL.encode EqualBench.QCIP.AVLBindings.impl_AVL_V0 EqualBench.QCIP.AVLBindings.impl_AVL_V1.

Definition C_AVL_STACK_refutationAt (x : EqualBench.QCIP.Domain.AVL.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.AVL.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.AVLBindings.impl_AVL_V0 (EqualBench.QCIP.Domain.AVL.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.AVLBindings.impl_AVL_V1 (EqualBench.QCIP.Domain.AVL.encode x) ob /\ oa <> ob.

Definition C_AVL_FACTOR_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.AVL.valid EqualBench.QCIP.Domain.AVL.encode EqualBench.QCIP.AVLBindings.impl_AVL_V0 EqualBench.QCIP.AVLBindings.impl_AVL_V2.

Definition C_AVL_FACTOR_refutationAt (x : EqualBench.QCIP.Domain.AVL.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.AVL.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.AVLBindings.impl_AVL_V0 (EqualBench.QCIP.Domain.AVL.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.AVLBindings.impl_AVL_V2 (EqualBench.QCIP.Domain.AVL.encode x) ob /\ oa <> ob.

Definition C_AVL_MIDDLE_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.AVL.valid EqualBench.QCIP.Domain.AVL.encode EqualBench.QCIP.AVLBindings.impl_AVL_V0 EqualBench.QCIP.AVLBindings.impl_AVL_V3.

Definition C_AVL_MIDDLE_refutationAt (x : EqualBench.QCIP.Domain.AVL.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.AVL.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.AVLBindings.impl_AVL_V0 (EqualBench.QCIP.Domain.AVL.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.AVLBindings.impl_AVL_V3 (EqualBench.QCIP.Domain.AVL.encode x) ob /\ oa <> ob.

Definition C_RING_COPY_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.Ring.valid EqualBench.QCIP.Domain.Ring.encode EqualBench.QCIP.RINGBindings.impl_RING_V0 EqualBench.QCIP.RINGBindings.impl_RING_V1.

Definition C_RING_COPY_refutationAt (x : EqualBench.QCIP.Domain.Ring.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.Ring.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.RINGBindings.impl_RING_V0 (EqualBench.QCIP.Domain.Ring.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.RINGBindings.impl_RING_V1 (EqualBench.QCIP.Domain.Ring.encode x) ob /\ oa <> ob.

Definition C_RING_REP_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.Ring.valid EqualBench.QCIP.Domain.Ring.encode EqualBench.QCIP.RINGBindings.impl_RING_V0 EqualBench.QCIP.RINGBindings.impl_RING_V2.

Definition C_RING_REP_refutationAt (x : EqualBench.QCIP.Domain.Ring.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.Ring.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.RINGBindings.impl_RING_V0 (EqualBench.QCIP.Domain.Ring.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.RINGBindings.impl_RING_V2 (EqualBench.QCIP.Domain.Ring.encode x) ob /\ oa <> ob.

Definition C_RING_FULL_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.Ring.valid EqualBench.QCIP.Domain.Ring.encode EqualBench.QCIP.RINGBindings.impl_RING_V0 EqualBench.QCIP.RINGBindings.impl_RING_V3.

Definition C_RING_FULL_refutationAt (x : EqualBench.QCIP.Domain.Ring.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.Ring.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.RINGBindings.impl_RING_V0 (EqualBench.QCIP.Domain.Ring.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.RINGBindings.impl_RING_V3 (EqualBench.QCIP.Domain.Ring.encode x) ob /\ oa <> ob.

Definition C_DIJK_SCAN_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.Dijkstra.valid EqualBench.QCIP.Domain.Dijkstra.encode EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V1.

Definition C_DIJK_SCAN_refutationAt (x : EqualBench.QCIP.Domain.Dijkstra.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.Dijkstra.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 (EqualBench.QCIP.Domain.Dijkstra.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V1 (EqualBench.QCIP.Domain.Dijkstra.encode x) ob /\ oa <> ob.

Definition C_DIJK_HEAP_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.Dijkstra.valid EqualBench.QCIP.Domain.Dijkstra.encode EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V2.

Definition C_DIJK_HEAP_refutationAt (x : EqualBench.QCIP.Domain.Dijkstra.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.Dijkstra.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 (EqualBench.QCIP.Domain.Dijkstra.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V2 (EqualBench.QCIP.Domain.Dijkstra.encode x) ob /\ oa <> ob.

Definition C_DIJK_SEEN_equivalence : Prop := EqualBench.QCIP.Execution.Equivalent EqualBench.QCIP.Domain.Dijkstra.valid EqualBench.QCIP.Domain.Dijkstra.encode EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V3.

Definition C_DIJK_SEEN_refutationAt (x : EqualBench.QCIP.Domain.Dijkstra.input) (oa ob : EqualBench.QCIP.Execution.observation) : Prop :=
  EqualBench.QCIP.Domain.Dijkstra.valid x /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V0 (EqualBench.QCIP.Domain.Dijkstra.encode x) oa /\ EqualBench.QCIP.Execution.run EqualBench.QCIP.DIJKSTRABindings.impl_DIJKSTRA_V3 (EqualBench.QCIP.Domain.Dijkstra.encode x) ob /\ oa <> ob.

Definition R_FAC_EQ_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 0) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V1.

Definition R_FAC_EQ_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 0 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V1 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_FAC_CEX_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 0) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V2.

Definition R_FAC_CEX_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 0 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.FACTORIALGoals.impl_FACTORIAL_V2 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_REV_EQ_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 1) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V1.

Definition R_REV_EQ_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 1 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V1 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_REV_CEX_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 1) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V2.

Definition R_REV_CEX_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 1 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.REVERSEGoals.impl_REVERSE_V2 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_SUM_EQ_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 2) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.SUMGoals.impl_SUM_V0 EqualBenchAlgorithms.SUMGoals.impl_SUM_V1.

Definition R_SUM_EQ_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 2 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SUMGoals.impl_SUM_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SUMGoals.impl_SUM_V1 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_SUM_CEX_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 2) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.SUMGoals.impl_SUM_V0 EqualBenchAlgorithms.SUMGoals.impl_SUM_V2.

Definition R_SUM_CEX_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 2 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SUMGoals.impl_SUM_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SUMGoals.impl_SUM_V2 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_MAT_EQ_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 3) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V1.

Definition R_MAT_EQ_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 3 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V1 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_MAT_CEX_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 3) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V2.

Definition R_MAT_CEX_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 3 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.MATRIXGoals.impl_MATRIX_V2 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_STR_EQ_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 4) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V1.

Definition R_STR_EQ_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 4 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V1 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_STR_CEX_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 4) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V2.

Definition R_STR_CEX_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 4 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.SEARCHGoals.impl_SEARCH_V2 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_QUE_EQ_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 5) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V1.

Definition R_QUE_EQ_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 5 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V1 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.

Definition R_QUE_CEX_equivalence : Prop := EqualBenchAlgorithms.Execution.Equivalent (EqualBenchAlgorithms.BasicDomain.valid 5) EqualBenchAlgorithms.BasicDomain.encode EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V2.

Definition R_QUE_CEX_refutationAt (x : list Z) (oa ob : EqualBenchAlgorithms.Execution.observation) : Prop :=
  EqualBenchAlgorithms.BasicDomain.valid 5 x /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V0 (EqualBenchAlgorithms.BasicDomain.encode x) oa /\ EqualBenchAlgorithms.Execution.run EqualBenchAlgorithms.QUEUEGoals.impl_QUEUE_V2 (EqualBenchAlgorithms.BasicDomain.encode x) ob /\ oa <> ob.
