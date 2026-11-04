# EqualBench: complex data-structure and function-call task cards

**Curator-only design draft.** Labels, proposed mutants, and witness seeds must be excluded from agent packages. These ten candidate families add 30 selected task slots to the original 12-family/24-slot inventory: 22 families and 54 slots in total. No new pair has been proved or refuted in this phase. BST, AVL, ring buffers and Dijkstra now have concrete derived C entries, precise domains/observations and twelve unproved targets in [tasks/qcip-core/TASKS.md](tasks/qcip-core/TASKS.md). That revision supersedes the broad cards below for these four families: it adds final map readouts, fixes the normalized ring API, and includes each Dijkstra provider in a single closed translation unit. These are refinements of existing slots, not twelve additional tasks. The source inspection report is in [research/qcip-candidate-review.md](research/qcip-candidate-review.md).

## Shared contract

Each task protects the entry function and the complete reachable implementation of every helper, including helpers in other translation units. A declaration plus an unproved functional contract is not a closed implementation. The agent may invent helper relations and prove them from supplied bodies. All required bodies, layouts, constants, and linking configuration are frozen with the task.

Core candidates use finite preallocated arenas, existing owned nodes, and bounded scratch arrays. Replacing an upstream allocator with arena code is an explicit source adaptation; the original allocating implementation remains an extension candidate. Diagnostic logging is either part of the declared observation or replaced by a visible no-op implementation in a clearly marked derived task. Copy helpers have concrete bodies. Allocation, I/O, or missing callees must never disappear silently behind source annotations.

L1--L4 describe provisional equivalence-proof obligations. L4 means composing several relations across recursive calls or module boundaries and mutable heap state; neither source length nor function count assigns this level automatically. W1--W3 describe witness discovery separately. Record heap shape, direct call edges, recursive strongly connected components, translation-unit count, and helper-body completeness as structural metadata.

For representation-changing tasks, compare client observations. Tree shape, cached metadata, parent arrays, and allocation addresses are observable only if the chosen API exposes them. Every task still requires safe termination on admitted inputs. Pointer-valued APIs use an explicit correspondence between caller-visible node identities.

| Family | Main contrasts | Selected slots | Proposed level | First implementation priority |
|---|---|---|---|---|
| `C-DLL` | helper calls / inline updates / indexed representation | 2 EQ + 1 CEX | L2--L3 / W2 | First complex slice |
| `C-RING` | two-span copy / byte loop / occupancy-count representation | 2 EQ + 1 CEX | L3 / W2--W3 | First complex slice |
| `C-TREE` | recursive mutation / explicit stack / queue traversal | 2 EQ + 1 CEX | L3 / W2 | First complex slice |
| `C-BST` | predecessor copy / successor transplant / rotation-based deletion | 2 EQ + 1 CEX | L3--L4 / W2 | Hard slice |
| `C-AVL` | recursive balancing / explicit path stack / rotation factoring | 2 EQ + 1 CEX | L3--L4 / W3 | Hard slice |
| `C-UF` | path compression / path halving / no compression | 2 EQ + 1 CEX | L3 / W2--W3 | First complex slice |
| `C-PQ` | heap / sorted array; repeated push / bottom-up build | 2 EQ + 1 CEX | L3 / W2 | First complex slice |
| `C-DIJK` | array scan / sorted priority queue / binary heap module | 2 EQ + 1 CEX | L4 / W2 | Hard slice |
| `C-EVAL` | recursive AST / explicit frames / factored operator calls | 2 EQ + 1 CEX | L2--L4 / W1--W2 | First complex slice |
| `C-PILE` | linked accumulation / cached aggregate / unchanged client | 2 EQ + 1 domain-sensitive CEX | L3--L4 / W1 | Web-source priority |

## C-DLL — intrusive doubly linked list clients

**Read source:** QCIP `OUTPUT/xizi/xizi_double_link_callpoint_specs/source/xizi_double_link_callpoint_specs.c` and `xizi_double_link_remove_node/source/xizi_double_link_remove_node.c`. Initialization and insertion bodies must be linked from their source cases before task freeze.

**Boundary:** a sentinel and at most 64 distinct preallocated nodes with stable logical IDs. Input is a legal finite operation sequence over initialize, insert-after, remove, length, forward traversal, and backward traversal. No operation dereferences a detached or foreign handle. Observe returned IDs/statuses and both traversal sequences. Scratch pointers and raw addresses outside the ID relation are hidden.

**Variants and tasks:** `R` calls the source-style list helpers; `E1` performs equivalent pointer updates in the client; `E2` stores next/previous links as bounded node indices. Compare `R/E1` for call decomposition and `R/E2` for representation replacement. `M` omits the successor's previous-link update during insertion; compare `R/M` for refutation.

**Witness seed:** insert node 1 after the sentinel, then node 2 after the sentinel, then enumerate backward. All followed links remain valid, but the mutant can omit node 2. A forward-only observation would miss this error. Expected proof work: preserve cyclic-list ownership and handle identity across each command.

## C-RING — ring-buffer read/write clients

**Read source:** QCIP `OUTPUT/xizi/xizi_circular_area_read/source/xizi_circular_area_read.c`, the write and force-write cases, and `xizi_circular_area_callpoint_specs/source/xizi_circular_area_callpoint_specs.c`. These are related source candidates, not already paired implementations; the current read and write copies contain different helper versions.

**Boundary:** capacity 1--64, initialized byte storage, valid read/write indices, disjoint caller buffers, and a finite sequence of nonzero read/write requests with explicit normal/forced-write mode. Observe return codes, bytes delivered, and the remaining logical FIFO sequence. Preserve the source's request truncation and error conventions; raw read/write indices are hidden across representations. A derived core task links concrete copy loops and an explicit no-op diagnostic function and uses caller-provided storage.

**Variants and tasks:** `R` uses split-into-two-spans copying and the full/empty flag; `E1` performs bytewise modular copying; `E2` uses an explicit occupancy count. Compare both replacements with `R`. `M` fails to distinguish full from empty when indices coincide.

**Witness seed:** capacity 2, write two distinct bytes, then read two bytes. A harder selected mutant can mishandle an interleaved read, wrapped write, and forced overwrite; its exact safe witness must be established during curation. Expected proof work: compose read/write/query helpers across the wrap boundary and preserve unobserved storage.

## C-TREE — recursive tree mutation versus explicit worklists

**Read source:** QCIP `OUTPUT/binaryTree/binaryTree_invert/source/binaryTree_invert.c` and `binaryTree_height/source/binaryTree_height.c`.

**Boundary:** an owned finite acyclic binary tree with at most 64 nodes and enough scratch storage. The client calls mirror mutation, then height and a read-only tree projection. Observe the returned height and the final ordered, labeled tree under the node correspondence. A shape projection preserves the left/right structure and node IDs even if the source nodes have no payload.

**Variants and tasks:** `R` recursively swaps and visits children; `E1` uses a pointer stack; `E2` uses a queue. Compare each with `R`. `M` skips processing the new right subtree after swapping at a node.

**Witness seed:** a root with a left child that itself has only a left child. The outputs can have the same height while their final tree shapes differ. Expected proof work: relate the unprocessed worklist to the recursive call frontier and preserve the original node footprint.

## C-BST — three deletion implementations behind a map API

**Read source:** QCIP `QCP_demos_LLM/bst_delete_rec2.c` and `bst_delete_new.c`; web candidate VST `progs/bst.c`, pinned in [web-source-audit.json](research/web-source-audit.json).

**Boundary:** a preallocated key/value BST with distinct keys, exclusively owned nodes, and finite delete/lookup command sequences. Observe lookup results as `option value`, not root pointer, tree topology, or the physical node selected for removal. Caller-held interior pointers are excluded. The core adapter uses a visible finite node-retirement implementation; the original `free` semantics is deferred. All source layout and retirement adaptations are recorded.

**Variants and tasks:** `R` recursively copies a predecessor key/value; `E1` iteratively transplants a successor; `E2` ports VST's rotation-based deletion to the chosen key/value layout before removal. VST's original pointer-valued payload layout is not silently treated as the QCP integer-valued layout. Compare `R/E1` and `R/E2`. `M` copies the predecessor key but retains the old value.

**Witness seed:** keys/values `(2,20),(1,10),(3,30)`, delete 2, then lookup 1. A membership-only observation would fail to expose the changed value. Expected proof work: relate different surviving shapes and cursor contexts while preserving the remaining map.

## C-AVL — balanced search trees with nested helper calls

**Read source:** QCIP `QCP_demos_LLM/avl_insert.c`; OUTPUT AVL insert, delete, and rotation cases provide additional source and boundary history. The OUTPUT insert is a documented repaired variant and must not be described as unchanged CRTOS code.

**Boundary:** finite insert/lookup traces starting from an empty tree, fixed node arena of sufficient size, and heights representable in the selected field width. The source demo ignores duplicate insertions; freeze that policy across all positive variants. Observe lookup values and return statuses. Topology and cached heights are hidden unless explicitly exposed by the API.

**Variants and tasks:** `R` uses recursive insert plus update/balance/rotation helpers; `E1` keeps an explicit ancestor stack and rebalances iteratively; `E2` factors double rotations differently while retaining the recursive API. Compare both to `R`. `M` clears the transferred middle subtree during a left rotation.

**Witness seed:** insert keys `1,0,3,2,4,5`, then lookup 2. The final rotation has a nonempty middle subtree; clearing it loses a key without needing an invalid dereference. Cached-height mistakes or omitted rotations are not automatically valid negative labels: a map-level observation requires a safe trace with an actual lookup/status difference. Expected proof work: compose subtree, height, cursor, and rotation relations over a recursive call chain.

## C-UF — union-find clients with different compression strategies

**Read source:** QCIP `QCP_demos_LLM/union_find_err_rel.c`. Its filename does not establish an implementation bug.

**Boundary:** singleton initialization of at most 64 elements followed by legal union/connected commands. Observe Boolean connectivity results only. Concrete representatives, parent arrays, and ranks may differ. The implementation contains a concrete connected wrapper that calls find; both arrays and all helper bodies are fixed.

**Variants and tasks:** `R` uses recursive full compression; `E1` uses path halving; `E2` uses an iterative root walk without compression. Pair each with `R`. `M` returns the immediate parent instead of the root.

**Witness seed:** with the source's equal-rank tie rule, union `(0,1)`, union `(2,3)`, union `(1,3)`, then query connected `(0,3)`. The command sequence builds a path with two edges. Expected proof work: maintain equivalence relations induced by different parent forests; equality of representative numbers is not the target.

## C-PQ — priority-queue replacement and bulk construction

**Read source:** QCIP `LLM_bench/Data_structures/priority_queue/priority_queue.c`, containing push/build/pop/heap_sort bodies. Its priority direction is maximum-first.

**Boundary:** at most 64 integers with duplicates allowed; valid push/pop/empty commands, or a fixed bulk-build-and-drain client. Observe popped integers in order and empty results. Internal heap-array order is hidden; any payload extension must pin a tie policy first.

**Variants and tasks:** `R` is the source-style heap; `E1` is a sorted-array priority queue for trace equivalence. In the bulk client, compare source `build` by repeated push with `E2`, a bottom-up heap builder, using the same pop interface. `M` always selects the left child while sifting down.

**Witness seed:** build from `[9,7,8,1]` and pop twice; the second popped value can differ. Expected proof work: compose build/push/pop relations and relate different internal arrangements while preserving duplicate multiplicity.

## C-DIJK — shortest paths with a replaceable queue module

**Read source:** QCIP `LLM_bench/Algorithms/Dijkstra/Dijkstra_linked_forward_star.c` plus `Dijkstra_priority_queue.c`. The latter implements a sorted-array minimum queue. The source pair has a real cross-file call boundary.

**Boundary:** a bounded graph with valid adjacency links, 1--10 vertices, nonnegative bounded weights, a source index, and a queue capacity justified for all admitted executions. Fix INF so admitted finite distances cannot collide with it or overflow. Observe the full distance vector and the unreachable marker. Do not compare processing order or predecessor choices under ties. Keep scratch/global queue memory outside the observation.

**Variants and tasks:** `R` uses the source queue-based algorithm; `E1` scans unsettled vertices directly; `E2` retains the client algorithm and replaces the sorted queue with a binary heap. Compare `R/E1` and `R/E2`. `M` suppresses a distance improvement once a vertex has been enqueued.

**Witness seed:** edges `0→1:10`, `0→2:1`, `2→1:1`, source 0. Expected proof work: compose graph traversal and queue operations, including stale entries; close all translation units rather than assume queue behavior from a supplied postcondition.

## C-EVAL — tagged AST interpreter versus explicit frames

**Read source:** QCIP `QCP_demos_LLM/eval.c`, which uses tags, a union, recursive calls, and Boolean short circuiting.

**Boundary:** an acyclic tagged AST with at most 64 nodes, valid variable indices, sufficient frame storage, and values in a range that prevents signed overflow. The core admitted syntax includes constants, variables, addition/subtraction, comparisons, Boolean operators, negation, and logical not; multiply/divide/modulo are left for a separately bounded extension. Observe the returned integer. AST and environment are read-only.

**Variants and tasks:** `R` is recursive; `E1` uses an explicit frame stack with the same short-circuit result convention; `E2` factors primitive operations into supplied helper bodies. Compare each with `R`. `M` implements logical AND as integer bitwise AND.

**Witness seed:** `AND(CONST 2, CONST 3)`. Eager evaluation alone is not a negative witness when the AST is pure and both sides terminate safely with equal outputs; do not manufacture a label from an unobserved evaluation order. Expected proof work: relate frame states to pending recursive evaluations and preserve Boolean normalization.

## C-PILE — actual module replacement and input-domain sensitivity

**Read web source:** VST `progs/VSUpile/pile.c`, `fast/fastpile.c`, and `triang.c` at the pinned commit in [web-source-audit.json](research/web-source-audit.json). The original examples allocate; a bounded-arena core adaptation is a separate derived program, and exact allocating sources remain extension candidates.

**Boundary:** command traces over add/count with defined integer arithmetic, or the supplied triangular-number client. Observe every count result and the client return value. List nodes, cached sum fields, and allocation addresses are hidden.

**Variants and three tasks:** `R` stores values in a linked list and traverses it for count; `E1` caches a sum and accepts only nonnegative additions that fit the integer range. (1) Under nonnegative bounded-prefix inputs and sufficient arena capacity, compare `R/E1`. (2) Compare `Triang_nth` linked against the two modules, under bounded `n`, as a client-level equivalence task. (3) Keep the same `R/E1` source pair but admit safe signed additions; require a counterexample certificate.

**Witness seed for task 3:** add `-1`, then count. The source cached implementation ignores the addition, while the linked representation retains it. The wider domain is an EqualBench comparison boundary; this is not a defect claim about the source verification, whose contracts restrict callers. The distinction between source reuse and a changed task is central here.

## Sampling and status

The ten families have 30 proposed task slots; the two C-PILE equivalence slots are correlated client/module contexts and remain one family. Source alternatives and proposed alternatives are explicitly distinguished above. No listed positive relation or negative witness has yet received an EqualBench kernel certificate. The original simple pilot stays at six families/12 slots. A first complex slice selects C-DLL, C-RING, C-TREE, C-UF, C-PQ, and C-EVAL (18 slots), before the harder families are instantiated.

The final 60--100 task target can select additional meaningful replacements or longer-trace mutants from these families. It must not count every possible implementation combination, or every client calling the same module, as an independent program family.
