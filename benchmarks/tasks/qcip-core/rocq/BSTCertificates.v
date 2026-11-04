(* Public disjunction goals. Packaging must rename variants neutrally

 * and exclude curator IDs, expected branches, and witness seeds. *)

From EqualBench.QCIP Require Import Domain Execution BSTBindings.

Theorem task_01 :
  Certificate BST.valid BST.encode impl_BST_V0 impl_BST_V1.
Abort.

Theorem task_02 :
  Certificate BST.valid BST.encode impl_BST_V0 impl_BST_V2.
Abort.

Theorem task_03 :
  Certificate BST.valid BST.encode impl_BST_V0 impl_BST_V3.
Abort.
