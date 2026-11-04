(* Curator-only expected branch goals. Abort closes an UNPROVED

 * declaration; it does not supply a certificate or an axiom. *)

From SpecLessBench.QCIP Require Import Domain Execution AVLBindings.

Theorem C_AVL_STACK :
  Equivalent AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V1.
Abort.

Theorem C_AVL_FACTOR :
  Equivalent AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V2.
Abort.

Theorem C_AVL_MIDDLE :
  Counterexample AVL.valid AVL.encode impl_AVL_V0 impl_AVL_V3.
Abort.
