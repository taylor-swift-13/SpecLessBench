(* Public disjunction goals. Packaging must rename variants neutrally

 * and exclude curator IDs, expected branches, and witness seeds. *)

From SpecLessBench.QCIP Require Import Domain Execution DIJKSTRABindings.

Theorem task_01 :
  Certificate Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V1.
Abort.

Theorem task_02 :
  Certificate Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V2.
Abort.

Theorem task_03 :
  Certificate Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V3.
Abort.
