(* Curator-only expected branch goals. Abort closes an UNPROVED

 * declaration; it does not supply a certificate or an axiom. *)

From EqualBench.QCIP Require Import Domain Execution RINGBindings.

Theorem C_RING_COPY :
  Equivalent Ring.valid Ring.encode impl_RING_V0 impl_RING_V1.
Abort.

Theorem C_RING_REP :
  Equivalent Ring.valid Ring.encode impl_RING_V0 impl_RING_V2.
Abort.

Theorem C_RING_FULL :
  Counterexample Ring.valid Ring.encode impl_RING_V0 impl_RING_V3.
Abort.
