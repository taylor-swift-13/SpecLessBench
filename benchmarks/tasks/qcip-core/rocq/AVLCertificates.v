(* Public disjunction goals. Packaging must rename variants neutrally

 * and exclude curator IDs, expected branches, and witness seeds. *)

From SpecLessBench.QCIP Require Import Domain Execution AVLBindings.

Theorem task_01 :
  Certificate AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V1.
Abort.

Theorem task_02 :
  Certificate AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V2.
Abort.

Theorem task_03 :
  Certificate AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V3.
Abort.
