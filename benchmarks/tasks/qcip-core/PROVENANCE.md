# Derived source provenance and adaptations

All entries here are **new derived task programs**, not byte-identical upstream copies. No claim of equivalence between an upstream artifact and its adaptation has been proved. Exact upstream snapshots, hashes and license lineage remain in `../../source-material/import-manifest.json`. QCIP revision: `fb3544dd349fe273b469e79828dd10b6a37fa184`; VST revision: `08cb56d32d9ce42505cf8167c4d0bd15fb119d9e`.

| Derived component | Source material / algorithm lineage | Explicit changes |
|---|---|---|
| BST V0 / V3 | QCIP `QCP_examples/QCP_demos_LLM/bst_delete_rec2.c` | New common node layout, names, bounded arena, live retirement marker, unique-key initialization, query/observation driver. V3 deliberately omits predecessor value assignment. |
| BST V1 | QCIP `QCP_examples/QCP_demos_LLM/bst_delete_new.c` | Same layout/arena/driver adaptation; successor transplant structure retained. |
| BST V2 | VST `progs/bst.c` | Port `delete/pushdown_left/turn_left` to integer-valued nodes; replace allocator/free with preallocated initialization/retirement; remove source main/client and pointer payloads. |
| AVL V0 | QCIP `QCP_examples/QCP_demos_LLM/avl_insert.c` | Rename fields/helpers, supply arena allocator and null-safe height helper, preserve unsigned-char heights, duplicate-ignore policy and strict child balance tests; add trace and inorder readout. |
| AVL V1 / V2 / V3 | Authored alternatives derived from that AVL family | V1 explicit ancestor cursor stack; V2 inline double rotations; V3 drop transferred middle subtree during left rotation. No OUTPUT repaired AVL variant is represented as an unchanged original here. |
| Ring V0 | QCIP `OUTPUT/xizi/xizi_circular_area_read/source/xizi_circular_area_read.c` and XiZi circular-area family design | New integrated read/write/force client. Use caller-owned inline storage, bounded integer indices instead of original uint8 fields, normalized code + actual-count observation, concrete copying, no operations function-pointer table, no diagnostic calls or strings. Force length bounded by capacity. This is not a literal port of a single frozen upstream write provider. |
| Ring V1 / V2 / V3 | Authored ring alternatives | Byte loop, occupancy count, and deliberate full-as-empty mutation, respectively. Same normalized API. |
| Dijkstra V0 | QCIP `QCP_examples/LLM_bench/Algorithms/Dijkstra/{Dijkstra_linked_forward_star.c,Dijkstra_priority_queue.c}` | Supply common headers/queue bodies in one included unit, rename symbols, reduce queue capacity from200005 to641, bound input edge list, add graph builder and distance observation. Preserve sorted-array min queue, stale check, strict relax, INF and overflow guard. |
| Dijkstra V1 / V2 / V3 | Authored alternatives | Scan algorithm; binary-min-heap module replacement; deliberate freeze-first-distance mutation. |

All source-system specifications and proof annotations are excluded from these C entries. Input/observation code is protected task code, not an independent declaration of the correct functional result. `Domain.v` only declares admissibility and serialization; it defines no map-update, FIFO, AVL-correctness or shortest-path oracle.

The original QCIP two-file Dijkstra client/provider boundary motivates module replacement. This task revision deliberately includes both bodies into one AST; experiments on separate compilation are future work. General heap allocation, reclamation, interior handles, allocator failure, logging and source-system trusted contracts are not silently inherited.

License texts and notices: see [NOTICE.md](NOTICE.md) and `licenses/`. A distributable task package must retain them with the source closure.

v0.2 adds independently executable Lean/Rocq re-encodings of each variant. Trees use immutable structural nodes, ring buffers use finite physical lists, and graph clients use lists plus explicit queue/heap operations. Representation and control-flow adaptations are disclosed in THREE-PLATFORM.md; they are not line-for-line translations or proven refinements. The original source lineage and license notices above also apply to source-derived algorithm ports. CompCert3.17 ASTs are generated from the unchanged C entries; manifests record binary/source/AST hashes and the localRocq9.2 environment. The old3.16 design interface remains historical. Its generic-globalenv mistake was found by actual type-checking, repaired in the v0.2 adapter, and archived in construction/repairs/61c3c7170831.
