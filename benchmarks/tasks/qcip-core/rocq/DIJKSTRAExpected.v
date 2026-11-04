(* Curator-only expected branch goals. Abort closes an UNPROVED

 * declaration; it does not supply a certificate or an axiom. *)

From EqualBench.QCIP Require Import Domain Execution DIJKSTRABindings.

Theorem C_DIJK_SCAN :
  Equivalent Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V1.
Abort.

Theorem C_DIJK_HEAP :
  Equivalent Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V2.
Abort.

Theorem C_DIJK_SEEN :
  Counterexample Dijkstra.valid Dijkstra.encode impl_DIJKSTRA_V0 impl_DIJKSTRA_V3.
Abort.
