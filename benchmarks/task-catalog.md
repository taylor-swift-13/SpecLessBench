# SpecLessBench task catalog (design draft)

**v0.8** adds Prim/Kruskal spanning forests and stable record sorting, with five contexts. Domains, targets and differential coverage are in [classics-core](tasks/classics-core/README.md). The active inventory has 29 groups and 63 contexts. The preceding Base64 source vectors and targets are in [base64-core](tasks/base64-core/README.md).

**Current v0.6 inventory** has 34 plan entries and 78 slots, with 26 concrete groups, 56 contexts, 168 platform instances and 82 Clight ASTs. The five new groups cover graph closure, scope, expiry, affine alignment and fixed-point resampling. Each group contributes a positive pair and a refutation pair. See [the numerical and systems tranche](tasks/systems-core/README.md) and [its index](systems-family-index.json).

**v0.5 materialization** added incremental framing, nested transactions and intrusive LRU caching, with six selected comparisons. See [stateful-core](tasks/stateful-core/README.md) and [stateful-family-index.json](stateful-family-index.json).

**v0.4 materialization:** 26 plan entries / 62 slots, with18 concrete implementation groups /40 contexts. The original22-entry/54-slot plan below is retained as design history. Eight groups are detailed in[boundaries-core](tasks/boundaries-core/README.md): TREE/UF/PQ/EVAL refine existing entries; TLV/tokenizer/block-decoder/path add four entries and eight slots. The evaluator's refined slot names are mapped in[boundary-family-index.json](boundary-family-index.json), not counted as extra slots.

**v0.2 rule:** every semantic context requires Lean, native Rocq and C/CompCert versions. Four materialized groups now provide12 contexts/36 platform instances, actual Clight ASTs and checked target types; see [three-platform construction](tasks/qcip-core/THREE-PLATFORM.md). Remaining contexts are candidates. Historical R-/C-IDs and track labels below describe source plans, not exemptions. Final proofs are deferred during construction; test-derived labels remain provisional. Constructors may revise programs/tasks with preserved issue and cost logs; solvers cannot edit frozen programs.

**v0.3.1 expansion:** six more existing entries (R-FAC/R-REV/R-SUM/R-MAT/R-STR/R-QUE) now have concrete three-platform implementations and12 contexts; see [algorithm tranche](tasks/algorithms-core/README.md). The [active registry](active-groups.json) contains10 implementation groups,24 unique context IDs,72 platform instances and34 actual Clight ASTs. The54-slot source plan is not a released independent-task count: remaining30 slots are unmaterialized or awaiting alias review. Equivalent source plans such as conceptual R-MAT/C-MAT ports must not inflate independent groups or duplicate identical pair/domain/observation contexts.

This catalog contains **22 candidate implementation-family entries and 54 selected task slots**, not a released dataset. The original 12 entries contribute 24 slots; ten complex entries contribute 30. Shared-source and conceptual cross-track entries must be assigned to common split groups before independent family counts are reported. Some proof probes exist, but no complete family in this catalog is reference-ready.

BST, AVL, ring buffers and Dijkstra have been refined into 16 concrete C entry programs and 12 unproved targets, with fixed domains, observations, generated/checked Clight ASTs and source hashes. See [the concrete task revision](tasks/qcip-core/TASKS.md). This refines their existing slots; no extra slots are counted. Reference certificates and isolated packaging remain pending. The concrete revision supersedes the broad candidate descriptions where they differ, including final map readouts, a normalized ring API and a single-unit Dijkstra provider build.

## Task construction unit

Each base family contains at least three immutable variants: a reference `R`, a replacement `E`, and a near-miss mutant `M`. The original slice selects two instances:

1. `FAMILY-EQ`: prove `R` and `E` observationally equivalent for every admitted input or initial state.
2. `FAMILY-CEX`: give a valid witness and prove that `R` and `M` have different observations.

Complex families select three contexts: usually two distinct replacement proofs and one refutation. C-PILE instead includes a client-level proof and a domain-sensitive refutation of the same real implementation pair. Proposed positive labels remain hypotheses until checked. The benchmark never treats a failed proof, timeout, or model judgment as evidence of inequivalence. We do not enumerate all pairwise combinations.

Difficulty labels are provisional: L1 uses direct induction/simple algebra; L2 needs an auxiliary invariant or representation relation; L3 connects distinct algorithms or semantic states; L4 composes several relations across recursive calls, modules, and heap updates. Function count alone does not assign L4. Counterexample discovery receives a separate W1--W3 label, from local mismatch to a longer state-reaching trace. Calibrate before model evaluation. Record implementation style, proof difficulty, witness difficulty, heap shape, call structure, track, and certificate polarity separately.

## Candidate families

| Family | Track | Fixed variants (`R` / `E` / `M`) | Observation boundary | EQ challenge | CEX seed | Level | Candidate provenance |
|---|---|---|---|---|---|---|---|
| `R-FAC` Factorial | Rocq | structural recursion / accumulator loop / predecessor-factor mutant | returned natural number | accumulator invariant and induction | input 1 | L1 | small canonical task; related recursion tasks can be sourced from VERINA/AlgoVeri after checking their exact files |
| `R-REV` List reversal | Rocq | direct recursion / accumulator reversal / wrong initial accumulator | returned list | generalized accumulator lemma | short list exposing the extra or misplaced element | L2 | canonical list-program family |
| `R-SUM` List sum | Rocq | structural fold / tail-recursive accumulator / skipped-element mutant | returned natural number | accumulator invariant | singleton or empty-list boundary, as selected by the mutant | L1 | canonical algorithm; potential VERINA/AlgoVeri analogue |
| `R-SORT` Stable sorting | Rocq | stable insertion sort / stable selection sort / ordinary unstable selection sort | exact output sequence of key-payload records | connect different ordering processes and preserve equal-key order | three records with duplicate keys | L3 | AlgoVeri sorting tasks and VERINA sorting-like tasks; preserve attribution and license notices |
| `R-MAT` Matrix multiplication | Rocq | row/column dot products / accumulation over the shared dimension / transposed-index mutant | returned matrix | relate nested traversals and index arithmetic | nonsymmetric compatible matrices | L3 | AlgoVeri `matrix_multiplication`; inspect source and contract before adapting |
| `R-STR` Substring search | Rocq | naive first-match search / KMP / faulty fallback mutant | returned first-match index or `None` | relate prefix-table state to the naive scan | short text/pattern forcing a fallback transition | L3 | AlgoVeri `string_search_naive` and `kmp`; source variants must be normalized to one observation interface |
| `R-QUE` Queue traces | Rocq | single-list queue / front-rear two-list queue / stale-rear mutant | sequence of dequeue results for an operation trace | representation relation and induction over commands | multi-step trace that triggers rear normalization twice | L2 | AlgoVeri queue operations; Vero's `QueueByList` / `QueueByTwoStacks` as concrete variants, subject to per-file provenance review |
| `R-SET` Set traces | Rocq | list-backed set / binary-search-tree set / faulty delete or duplicate handling | membership-result trace for an operation sequence | representation invariant across insert/delete/search | short trace exposing a missing or retained key | L3 | AlgoVeri `bst_*` tasks; do not use their supplied function-level contracts as SpecLessBench goals |
| `C-LOOP` Loop fusion | C/Clight | nested row/column loops / flattened loop / last-cell-skipping mutant | return value and designated output slice | align different control-flow schedules | smallest shape where the last cell is skipped | L2 | hand-authored C variant from a fixed bounded-array template; no copied source selected yet |
| `C-REV` Array reversal | C/Clight | temporary-buffer reverse / in-place swaps / endpoint mutant | return value and first `n` cells | relate buffer writes to in-place state updates | length two or three, depending on the mutant | L2 | canonical C transformation; candidate for the pilot |
| `C-MAT` Matrix multiplication | C/Clight | row/column dot product / shared-dimension accumulation / transposed-index mutant | return value and designated output matrix | loop-nest transformation and memory-state relation | nonsymmetric compatible matrices | L3 | bounded-array C family; conceptually paired with `R-MAT` |
| `C-MOVE` Overlapping copy | C/Clight | temporary-buffer copy / direction-aware copy / always-forward copy | return value and designated array slice | aliasing, overlap cases, and memory-state relation | destination-after-source overlapping range | L3 | hand-authored bounded-array C family; CompCert semantics and all bounds must be pinned |

For Rocq list/array-like problems, the admissible shape conditions are part of the input boundary. For C tasks, the first release uses fixed-capacity arrays, bounded indices, nonoverflowing integer values, and no I/O or dynamic allocation. Each task names exactly which return value and memory cells are observed. Unobserved stack slots and temporary storage are intentionally outside the relation.

## Complex data structures and function calls

The ten entries below add 30 slots. Detailed variants, code provenance, helper gaps, and proposed witnesses are in [complex-task-cards.md](complex-task-cards.md). Source facts come from the read-only [QCIP review](research/qcip-candidate-review.md), its 28-file hash inventory, and pinned VST web sources. Replacements and witnesses remain candidate designs.

| Family | Source implementation and call structure | Selected replacements / task context | Observations | Slots | Level |
|---|---|---|---|---|---|
| `C-DLL` | XiZi intrusive-list helper clients | helper calls vs inline updates; pointer links vs indexed links; stale-backlink mutant | status/node IDs, forward and backward traversal | 3 | L2--L3 |
| `C-RING` | XiZi read/write → state queries / split-copy helpers | bulk copy vs byte loop; flag vs occupancy count; full/empty mutant | codes, delivered bytes, logical FIFO | 3 | L3 |
| `C-TREE` | OUTPUT recursive mirror and height | recursion vs stack; recursion vs queue; skipped-subtree mutant | labeled tree projection and height | 3 | L3 |
| `C-BST` | QCP predecessor / successor deletion; VST rotation-based deletion | two deletion replacements; wrong value-copy mutant | key/value lookup trace | 3 | L3--L4 |
| `C-AVL` | insert → balance → double rotation → rotation → height update | iterative path stack; alternative rotation factoring; lost-middle-subtree mutant | lookup values and statuses | 3 | L3--L4 |
| `C-UF` | union → recursive find | full compression vs halving vs no compression; one-hop mutant | connected-query trace | 3 | L3 |
| `C-PQ` | build → push; heap_sort → build/pop | heap vs ordered array; repeated push vs bottom-up build; wrong-child mutant | priority extraction trace | 3 | L3 |
| `C-DIJK` | graph client + separate sorted-array queue translation unit | array-scan algorithm; binary-heap module; seen-on-enqueue mutant | distance vector / unreachable marker | 3 | L4 |
| `C-EVAL` | tagged union AST and recursive evaluator | explicit frames; factored operator helpers; logical/bitwise mutant | returned integer | 3 | L2--L4 |
| `C-PILE` | VST linked-list module / cached-sum module / client | module replacement; client preservation; widened-domain refutation | count trace / client result | 3 | L3--L4 |

These tasks use complete linked implementations. The core may derive finite-arena variants from allocating sources, but those are marked adaptations; the original allocating code is an extension candidate. Logs and library calls need visible implementations or an explicit semantic trust boundary. They cannot be silently removed through annotations.

## Initial pilot slice

The pilot plan selects six families and two polarities per family: `R-FAC`, `R-MAT`, `R-STR`, `R-QUE`, `C-LOOP`, and `C-REV`. This gives four Rocq families and two Clight families, with L1, L2, and L3 challenges. The alternate `R-REV` proof is currently an extra validated probe, not a replacement for the pilot's planned string or matrix tasks. `R-MAT`/`C-MAT` and `R-REV`/`C-REV` are conceptual cross-track pairs in the next tranche; the pilot alone cannot support a causal track comparison.

The earlier simple and complex slices are curation plans. The inventory has22 entries/54 semantic contexts, with60--100 selected contexts still planned, each requiring three platforms. Current construction stops before final proofs; a successful solve later still requires a checked certificate. Unmaterialized rows cannot be counted as completed tasks.

## Source adaptation and split rules

Source programs are candidate material, not ground truth. For every adapted family, the curator records the upstream repository, commit or release, exact file/task identifier, license, attribution, code changes, and any inherited test/spec artifacts. The agent-facing task omits any separate function-level postcondition from the source benchmark. Source specs and tests may inform boundary discovery but cannot serve as proof targets or replace pairwise certificates.

All variants, domain variants, and clients of the same implementation family stay in one split. A `split_group_id` also joins conceptual cross-track ports and families sharing distinctive task-specific implementations or helpers. Common environment libraries alone do not join unrelated families. Report the final number of independent split groups as well as implementation-family entries; resample at the group level when entries are correlated. Source-derived and newly written programs are reported separately.

## Status vocabulary

- `candidate`: family idea and comparison boundary sketched.
- `prototype`: at least one representative proof or counterexample artifact has been checked locally; this does not imply the family is complete.
- `reference-ready`: implementations, boundary, fixed target, source record, and reference certificates are all pinned and reproducibly checked.
- `evaluation-ready`: reference-ready plus isolated editable slots, clean rebuild, grader, and split metadata.

Current pending three-platform problems are tracked in [active-groups.json](active-groups.json); earlier proved probes remain in [`pilot/README.md`](pilot/README.md). Concrete construction status does not imply a final proof or isolated evaluation package.
