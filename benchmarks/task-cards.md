# SpecLessBench candidate task cards

This file covers the original 12-family/24-slot base slice. Ten additional data-structure and function-call families (30 slots) are in [complex-task-cards.md](complex-task-cards.md); see the combined [catalog](task-catalog.md).

**Curator-only draft; do not include this file in an agent-facing task package.** These cards contain intended labels and witness seeds. The eventual benchmark runner must render sanitized prompts from separate task assets, keeping polarity labels, seeds, and reference certificates in evaluator-only metadata. The cards define candidate inputs, implementation pairs, and observations for the 12-family design tranche; they are not executable tasks. Every candidate must still be implemented, frozen, source-audited, and supplied with a checked equivalence or counterexample certificate before evaluation.

For each family, `R` is the behavior reference, `E` is a replacement proposed for the positive instance, and `M` is a near-miss mutant used for the negative instance. The task goal contains only the pair relation and its input/observation boundary. It does not contain a third function that dictates the intended answer.

## Native Rocq

### R-FAC — recursive versus accumulator factorial (L1)

- **Input and observation:** `n : nat`; observe the returned natural number. All inputs are admitted.
- **R / E:** direct recursive product / accumulator implementation initialized with `1`.
- **M:** in the successor case, multiply the accumulator by predecessor `k` instead of `S k`.
- **Positive pair:** compare `R n` and `E n` for every `n`.
- **Negative seed:** `n = 1`; the mutant multiplies by zero where the reference multiplies by one.
- **Witness level:** W1, a one-step local arithmetic discrepancy.
- **Reasoning label:** accumulator invariant and induction. Positive and negative Rocq prototypes already exist; they still need packaging as protected benchmark tasks.

### R-REV — direct versus accumulator list reversal (L2)

- **Input and observation:** any finite list `xs : list A`; observe the returned list exactly.
- **R / E:** recursive reversal using append / tail-recursive reversal with an initially empty accumulator.
- **M:** run the accumulator helper with `xs` as its initial accumulator instead of `[]`.
- **Positive pair:** compare `R xs` and `E xs` for all lists.
- **Negative seed:** any singleton list; the mutant returns an extra copy of the element.
- **Witness level:** W1, a singleton exposes the wrong initial state.
- **Reasoning label:** generalize the accumulator relation and establish the append/reversal bridge. The positive relation has already been checked as a standalone probe; the mutant task is a candidate.

### R-SUM — structural sum versus tail-recursive sum (L1)

- **Input and observation:** any finite list of natural numbers; observe the returned natural number.
- **R / E:** head-plus-recursive-tail sum / accumulator loop initialized at zero.
- **M:** omit the head element at the first recursive step.
- **Positive pair:** compare the two sums for every list.
- **Negative seed:** singleton `[1]`.
- **Witness level:** W1, one element suffices.
- **Reasoning label:** one accumulator invariant; selected as a second low-difficulty family to calibrate L1.

### R-SORT — stable insertion sort versus stable selection sort (L3)

- **Input and observation:** any finite list of records `(key : nat, payload : nat)`; observe the exact returned sequence, including payload order among equal keys.
- **R / E:** stable insertion sort / stable selection sort that extracts the first minimum and preserves the remaining record order.
- **M:** ordinary selection sort that swaps the first minimum into place and may reorder equal-key records.
- **Positive pair:** compare exact output sequences for all lists.
- **Negative seed:** `[(2,0),(2,1),(1,2)]`; ordinary selection sort can move the later minimum ahead of the equal-key records and change their payload order.
- **Witness level:** W2, requires duplicate keys and a later smaller key.
- **Reasoning label:** connect distinct sorting procedures while preserving stability. Exact payload order makes the mutant behavior observable.

### R-MAT — matrix multiplication by row dot products versus shared-dimension accumulation (L3)

- **Input and observation:** dimensions `m,n,k > 0`; nested-list matrices `A` and `B` with exactly `m` rows of length `k` and `k` rows of length `n`, over `Z`; observe the exact `m × n` result matrix.
- **R / E:** compute each output cell as a dot product / initialize output cells to zero and accumulate one shared-dimension contribution at a time.
- **M:** use `B[j][q]` instead of `B[q][j]` in each product term, transposing the access pattern.
- **Positive pair:** compare result matrices for all well-shaped inputs.
- **Negative seed:** `m=1,n=k=2`, `A=[[1,0]]`, `B=[[1,2],[3,4]]`; the reference returns `[[1,2]]`, while the mutant returns `[[1,3]]`.
- **Witness level:** W2, requires a nonsymmetric matrix and compatible dimensions that expose the transposed index.
- **Reasoning label:** relate nested traversals, indexing, and accumulator state. AlgoVeri's `matrix_multiplication` is a candidate source; its own function-level contract is not the SpecLessBench goal.

### R-STR — naive first-match search versus KMP (L3)

- **Input and observation:** text and pattern are finite lists of 8-bit values; an empty pattern returns `Some 0`; observe `option nat` with the first match index or `None`.
- **R / E:** naive candidate-start scan / KMP with a prefix table.
- **M:** on a mismatch after a partial match, reset the matched-prefix length to zero and advance the text position without reprocessing the mismatching byte.
- **Positive pair:** compare the returned option for every text/pattern pair.
- **Negative seed:** text `aaab`, pattern `aab`; correct KMP and the naive scan find index `1`, while the mutant can skip the overlapping start.
- **Witness level:** W2, requires an overlapping match after a fallback transition.
- **Reasoning label:** establish the meaning of the KMP prefix state and fallback transition. AlgoVeri's `string_search_naive` and `kmp` are candidate source tasks; normalize them to this byte and empty-pattern boundary before pairing.

### R-QUE — list queue versus two-list queue over operation traces (L2)

- **Input and observation:** finite command sequence over `enqueue(n)` and `dequeue`; observe the ordered sequence of `option nat` values returned by dequeue commands. Dequeue on an empty queue returns `None` and leaves the queue unchanged.
- **R / E:** one-list queue / front-rear two-list queue with rear normalization by reversal when the front becomes empty.
- **M:** reverse the rear list into the front when needed but forget to clear the rear list afterward.
- **Positive pair:** compare dequeue-result traces for every command sequence.
- **Negative seed:** `enqueue(1); enqueue(2); dequeue; dequeue; dequeue`; the correct trace is `[Some 1, Some 2, None]`, while the mutant can replay a stale rear element.
- **Witness level:** W3, the defect appears only after normalization and a second empty-front transition.
- **Reasoning label:** maintain a representation relation across commands. Candidate source variants include AlgoVeri queue operations and Vero's `QueueByList` / `QueueByTwoStacks`; review exact provenance and notices first.

### R-SET — list set versus binary-search-tree set over operation traces (L3)

- **Input and observation:** finite command sequence over `insert(n)`, `delete(n)`, and `member(n)`; observe the Boolean result of each membership query. Duplicate insertion and deletion of absent keys are no-ops.
- **R / E:** list-backed set / binary-search-tree set.
- **M:** tree deletion leaves a node with two children in place.
- **Positive pair:** compare membership traces for every command sequence.
- **Negative seed:** insert `2`, `1`, `3`; delete `2`; query membership of `2`.
- **Witness level:** W2, requires constructing and then deleting a two-child root.
- **Reasoning label:** maintain a representation invariant across state transitions. AlgoVeri's `bst_insert`, `bst_search`, and `bst_delete` are candidate source files; their supplied specs are excluded from the prompt.

## C via Clight

All C candidates use fixed capacity `CAP = 64`, bounded indices, integer ranges that rule out signed overflow, and no external calls or I/O. Both programs in a family use the same function signature. The protected C source and `clightgen` output must be hashed together. Initial memory relations require corresponding input values and disjoint regions where needed; observation projects only the return value and named output cells.

### C-LOOP — nested versus flattened elementwise loops (L2)

- **Input and observation:** positive dimensions `m,n`, `m*n <= CAP`; two read-only input slices and one disjoint output slice; each input value lies in `[-16,16]`. Observe the returned cell count and `out[0..m*n)`.
- **R / E:** nested row/column loops writing `out[i*n+j] = a[i*n+j] + b[i*n+j]` / one flattened loop over `m*n` cells.
- **M:** process only positions satisfying `index + 1 < m*n`.
- **Positive pair:** compare return value and output slice for every admitted initial state.
- **Negative seed:** `m=n=1`, `a[0]=1`, `b[0]=2`.
- **Witness level:** W1, a one-cell input exposes the skipped final write.
- **Reasoning label:** relate loop counters and output-memory updates.

### C-REV — temporary-buffer versus in-place array reversal (L2)

- **Input and observation:** `0 <= n <= CAP`; initial array values are unrestricted `int` values. Observe returned length and `a[0..n)`.
- **R / E:** copy the reversed prefix through a local temporary array / swap symmetric positions in place.
- **M:** stop the swap loop when `i+1 < n/2`, omitting a required swap for even lengths.
- **Positive pair:** compare return value and the designated array prefix for every admitted array and length.
- **Negative seed:** `n=2` and two distinct initial elements.
- **Witness level:** W1, a single required swap is omitted.
- **Reasoning label:** relate temporary writes to in-place memory updates. This is one of the two C families in the initial pilot.

### C-MAT — row/column versus shared-dimension C matrix multiplication (L3)

- **Input and observation:** positive dimensions `m,n,k <= 8` with flattened regions within `CAP`; `A`, `B`, and output are disjoint; input elements lie in `[-1,1]`; output starts at zero. Both functions return `0`; observe the return value and the first `m*n` output cells.
- **R / E:** for each `(i,j)`, compute a local dot product and store it / loop over `(i,k,j)` and accumulate each product into output.
- **M:** use `B[j*k+q]` instead of `B[q*n+j]` in each product term, transposing the access pattern (the witness has `n=k`).
- **Positive pair:** compare return and output memory for all admitted initial states.
- **Negative seed:** `m=1,n=k=2`, `A=[1,0]`, `B=[1,2,3,4]`, output initialized to zero; the reference returns `[1,2]`, while the mutant returns `[1,3]`.
- **Witness level:** W2, requires a nonsymmetric matrix and a rectangular first dimension.
- **Reasoning label:** combine loop-nest transformation with memory-state reasoning. This family is conceptually paired with `R-MAT` for a cross-track comparison.

### C-MOVE — temporary-buffer versus direction-aware overlapping copy (L3)

- **Input and observation:** one fixed array of capacity `CAP`; source and destination ranges satisfy `src+len <= CAP` and `dst+len <= CAP`; overlap is allowed. Observe return count and resulting array slice.
- **R / E:** copy source to a local temporary array then write destination / copy backward when `dst > src` overlaps the source and forward otherwise.
- **M:** always copy forward.
- **Positive pair:** compare return value and array slice for every admitted index triple and initial array.
- **Negative seed:** array `[1,2,3]`, `src=0`, `dst=1`, `len=2`.
- **Witness level:** W1, a two-element overlapping copy is enough.
- **Reasoning label:** reason about aliasing and old memory values across writes.

## Matching and difficulty calibration

L1--L3 label the universal equivalence proof obligation. W1--W3 independently label counterexample discovery: W1 is a local discrepancy, W2 requires a nontrivial shape or overlap, and W3 requires a longer state-reaching trace. These scales are deliberately separate; a short witness can refute an L3 equivalence claim. The six-family pilot has W1 and W2 examples but only one W3 queue candidate, so it cannot estimate polarity effects reliably. `R-MAT`/`C-MAT` and `R-REV`/`C-REV` are intended conceptual pairs. Their representations and observation boundaries still differ, so track comparisons are descriptive unless a larger paired set supports a controlled analysis.

Two curators should independently assign implementation-style labels and predict proof obligations before agent runs. For each family, record a fixed expert proof-attempt budget, whether a helper lemma or invariant was required, counterexample witness size, and any boundary revisions. Resolve level disagreements before freezing the test split. Model outcomes must not be used to retrofit initial difficulty labels.
