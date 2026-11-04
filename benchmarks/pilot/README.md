# SpecLessBench 12-task pilot plan

This is a curator design file containing polarity labels and candidate counterexample seeds. It must not be copied into an agent-facing evaluation package.

This pilot is the simple slice of the larger inventory in [`../task-catalog.md`](../task-catalog.md). The catalog now has 22 candidate implementation-family entries/54 task slots. This file tracks the original six-family/12-slot plan; a separate six-family/18-slot complex slice is specified in [`../complex-task-cards.md`](../complex-task-cards.md).

SpecLessBench compares implementations directly, without a separate declarative functional specification. A task gives the two implementations, a valid input/state boundary, and an observation interface. The expected answer is a checked equivalence proof for a positive pair or a checked counterexample for a negative pair. A timeout or failed proof is never evidence of inequivalence.

The pilot has 12 task instances grouped into six families. Each family should contain at least three implementations: a reference, one or more structurally different replacements, and a near-miss mutant. We select a positive pair and a negative pair per family; we do not count every implementation combination as a new task.

| IDs | Track | Family and implementation variants | Positive task | Negative task | Challenge / difficulty | Status |
|---|---|---|---|---|---|---|
| R-FAC-P / R-FAC-N | Native Rocq | Recursive factorial, accumulator factorial, off-by-one accumulator mutant | Prove recursive and accumulator versions equal | Prove the mutant differs on a valid input | Induction and accumulator invariant; L1 | Prototype validated |
| R-MAT-P / R-MAT-N | Native Rocq | Direct matrix product, row/column or transposed formulation, indexing mutant | Prove two formulations equal | Produce a valid matrix counterexample for the mutant | Index relations, dimensions, arithmetic; L3 | Candidate |
| R-STR-P / R-STR-N | Native Rocq | Naive substring search, KMP, prefix/boundary mutant | Prove search results equal | Produce a string/pattern witness for the mutant | State invariant and prefix-table meaning; L3 | Candidate |
| R-QUE-P / R-QUE-N | Native Rocq | Single-list queue, two-list queue, operation-order mutant | Prove observable operation sequences agree | Give a finite operation sequence with different observations | Representation relation and sequence induction; L2–L3 | Candidate |
| C-LOOP-P / C-LOOP-N | C／Clight | Nested loops, fused loop, boundary mutant | Prove safe terminating behavior agrees | Give a valid finite input with different outputs | Loop invariants and control-flow alignment; L2 | Candidate |
| C-REV-P / C-REV-N | C／Clight | Buffer reverse, in-place reverse, endpoint mutant | Prove return/output-memory observations agree | Give a valid array state with different output memory | Index relation and memory updates; L2 | Candidate |

`L1` denotes a direct induction or small witness; `L2` requires an auxiliary invariant or representation relation; `L3` requires connecting different algorithms or semantic states. These are initial hypotheses and should be recalibrated after proof attempts and model runs.

## Current verified probes

- `../prototypes/native_rocq/FactorialEquivalent.v`: recursive factorial and accumulator factorial equality proof, checked by Coq 8.20.1.
- `../prototypes/native_rocq/FactorialCounterexample.v`: off-by-one accumulator mutant counterexample, checked by Coq 8.20.1.
- `../prototypes/native_rocq/ReverseEquivalent.v`: direct recursive reverse and accumulator reverse equality proof, checked by Coq 8.20.1. This is an additional probe and not one of the six initial pilot families yet.

The pilot matrix is a curation plan, not a claim that all listed tasks exist. Matrix, string, queue, and C tasks need exact fixed implementations, nonempty input domains, observation contracts, and kernel-checked reference certificates before becoming `reference-ready`.

## Scale and evaluation plan

Use the 12-task pilot to debug the contract, difficulty labels, and agent interface. For a submission-scale benchmark, target 20–30 families and 60–100 selected task instances, with complete family-level splits. Candidate evaluation: 6–8 pinned agent configurations spanning general coding agents and proof-focused systems; run pass@1 on every task, then a fixed iterative-repair budget on the pilot and a stratified harder subset. Report certificate success overall and separately for equivalence proofs and counterexample proofs. Freeze exact models, prompts, and budgets near the evaluation date; the model landscape changes quickly.

This scale is informed by VERINA (189 Lean tasks, modular code/spec/proof evaluation), Vero (43 repository instances, proof-only and code-and-proof modes, plus formal audit routes), and AlgoVeri (77 aligned classical-algorithm tasks across Dafny, Verus, and Lean). SpecLessBench takes their curation, repair-budget, and audit practices as references while keeping its task distinct: no separate function-level postcondition is supplied, and the scored artifact is an equivalence proof or a formally established counterexample between implementations. VeriEquivBench is a closer methodological neighbor: it uses formal equivalence checks to assess generated code/specification pairs, whereas SpecLessBench gives both implementations in advance and scores a direct program-to-program certificate. See the paper's related-work section and [`../sources.md`](../sources.md) for the source and licensing policy.
