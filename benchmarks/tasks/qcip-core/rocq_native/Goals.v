From EqualBench.QCIP Require Import Domain.

From EqualBenchNative Require Import Native.

Theorem C_BST_SUCCESSOR : Equivalent BST.valid (fun x => bst 0 (BST.encode x)) (fun x => bst 1 (BST.encode x)).
Abort.

Theorem C_BST_SUCCESSOR_certificate : Certificate BST.valid (fun x => bst 0 (BST.encode x)) (fun x => bst 1 (BST.encode x)).
Abort.

Theorem C_BST_ROTATE : Equivalent BST.valid (fun x => bst 0 (BST.encode x)) (fun x => bst 2 (BST.encode x)).
Abort.

Theorem C_BST_ROTATE_certificate : Certificate BST.valid (fun x => bst 0 (BST.encode x)) (fun x => bst 2 (BST.encode x)).
Abort.

Theorem C_BST_VALUE : Counterexample BST.valid (fun x => bst 0 (BST.encode x)) (fun x => bst 3 (BST.encode x)).
Abort.

Theorem C_BST_VALUE_certificate : Certificate BST.valid (fun x => bst 0 (BST.encode x)) (fun x => bst 3 (BST.encode x)).
Abort.

Theorem C_AVL_STACK : Equivalent AVL.valid (fun x => avl 0 (AVL.encode x)) (fun x => avl 1 (AVL.encode x)).
Abort.

Theorem C_AVL_STACK_certificate : Certificate AVL.valid (fun x => avl 0 (AVL.encode x)) (fun x => avl 1 (AVL.encode x)).
Abort.

Theorem C_AVL_FACTOR : Equivalent AVL.valid (fun x => avl 0 (AVL.encode x)) (fun x => avl 2 (AVL.encode x)).
Abort.

Theorem C_AVL_FACTOR_certificate : Certificate AVL.valid (fun x => avl 0 (AVL.encode x)) (fun x => avl 2 (AVL.encode x)).
Abort.

Theorem C_AVL_MIDDLE : Counterexample AVL.valid (fun x => avl 0 (AVL.encode x)) (fun x => avl 3 (AVL.encode x)).
Abort.

Theorem C_AVL_MIDDLE_certificate : Certificate AVL.valid (fun x => avl 0 (AVL.encode x)) (fun x => avl 3 (AVL.encode x)).
Abort.

Theorem C_RING_COPY : Equivalent Ring.valid (fun x => ring 0 (Ring.encode x)) (fun x => ring 1 (Ring.encode x)).
Abort.

Theorem C_RING_COPY_certificate : Certificate Ring.valid (fun x => ring 0 (Ring.encode x)) (fun x => ring 1 (Ring.encode x)).
Abort.

Theorem C_RING_REP : Equivalent Ring.valid (fun x => ring 0 (Ring.encode x)) (fun x => ring 2 (Ring.encode x)).
Abort.

Theorem C_RING_REP_certificate : Certificate Ring.valid (fun x => ring 0 (Ring.encode x)) (fun x => ring 2 (Ring.encode x)).
Abort.

Theorem C_RING_FULL : Counterexample Ring.valid (fun x => ring 0 (Ring.encode x)) (fun x => ring 3 (Ring.encode x)).
Abort.

Theorem C_RING_FULL_certificate : Certificate Ring.valid (fun x => ring 0 (Ring.encode x)) (fun x => ring 3 (Ring.encode x)).
Abort.

Theorem C_DIJK_SCAN : Equivalent Dijkstra.valid (fun x => dijkstra 0 (Dijkstra.encode x)) (fun x => dijkstra 1 (Dijkstra.encode x)).
Abort.

Theorem C_DIJK_SCAN_certificate : Certificate Dijkstra.valid (fun x => dijkstra 0 (Dijkstra.encode x)) (fun x => dijkstra 1 (Dijkstra.encode x)).
Abort.

Theorem C_DIJK_HEAP : Equivalent Dijkstra.valid (fun x => dijkstra 0 (Dijkstra.encode x)) (fun x => dijkstra 2 (Dijkstra.encode x)).
Abort.

Theorem C_DIJK_HEAP_certificate : Certificate Dijkstra.valid (fun x => dijkstra 0 (Dijkstra.encode x)) (fun x => dijkstra 2 (Dijkstra.encode x)).
Abort.

Theorem C_DIJK_SEEN : Counterexample Dijkstra.valid (fun x => dijkstra 0 (Dijkstra.encode x)) (fun x => dijkstra 3 (Dijkstra.encode x)).
Abort.

Theorem C_DIJK_SEEN_certificate : Certificate Dijkstra.valid (fun x => dijkstra 0 (Dijkstra.encode x)) (fun x => dijkstra 3 (Dijkstra.encode x)).
Abort.
