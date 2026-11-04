(* Public disjunction goals. Packaging must rename variants neutrally

 * and exclude curator IDs, expected branches, and witness seeds. *)

From SpecLessBench.QCIP Require Import Domain Execution RINGBindings.

Theorem task_01 :
  Certificate Ring.valid Ring.encode impl_RING_V0 impl_RING_V1.
Abort.

Theorem task_02 :
  Certificate Ring.valid Ring.encode impl_RING_V0 impl_RING_V2.
Abort.

Theorem task_03 :
  Certificate Ring.valid Ring.encode impl_RING_V0 impl_RING_V3.
Abort.
