(* Curator-only expected branch goals. Abort closes an UNPROVED

 * declaration; it does not supply a certificate or an axiom. *)

From SpecLessBench.QCIP Require Import Domain Execution BSTBindings.

Theorem C_BST_SUCCESSOR :
  Equivalent BST.valid BST.encode impl_BST_V0 impl_BST_V1.
Abort.

Theorem C_BST_ROTATE :
  Equivalent BST.valid BST.encode impl_BST_V0 impl_BST_V2.
Abort.

Theorem C_BST_VALUE :
  Counterexample BST.valid BST.encode impl_BST_V0 impl_BST_V3.
Abort.
