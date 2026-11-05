# SpecLessBench

SpecLessBench is a benchmark for proving behavioral equivalence between two fixed program implementations without a separate functional specification.

Given an input domain and an observation model, an agent must either prove that the implementations agree on every valid input or provide a formally checked counterexample. A reference implementation serves as the executable description of the behavior to preserve.

## Benchmark

The frozen pilot contains **71 task contexts across 30 families**, with implementations and proof goals for three platforms. The entire factorial family is reserved for public gold-standard examples and excluded from evaluation, leaving **69 contexts across 29 families** eligible for the evaluation set:

- **Lean:** native functional implementations.
- **Rocq:** native functional implementations.
- **C / CompCert:** C implementations represented by Clight ASTs and evaluated using CompCert semantics.

Tasks cover classical algorithms, data structures, and programs adapted from real-world sources. Observations are task-specific: for example, a C task may compare return values and selected output memory rather than entire final memories.

## Status

SpecLessBench is a research prototype. The pilot's three-platform definitions and goal types have been checked, and its implementations have undergone differential testing. Final task proofs are not provided.

The isolated evaluator is under development. Currently, one Lean equivalence task is connected to the scorer; the remaining tasks and counterexample branch are not yet available for evaluation. The existing public sources may contain answer hints, so the repository is not yet a leakage-free evaluation release.

## Getting started

The following checks run in the project's existing WSL environment:

```bash
python3 scripts/pilot/verify_freeze.py
python3 scripts/pilot/prepare_factorial.py
python3 scripts/pilot/test_real_factorial.py
```

These commands require the pinned toolchains and private pilot metadata on the original machine; a standalone installation and portable release are not yet available. See the [pilot documentation](benchmarks/pilot/README.md) for details.

## Repository

- [`benchmarks/tasks/`](benchmarks/tasks/) — implementations, domains, and proof goals.
- [`benchmarks/pilot/`](benchmarks/pilot/) — frozen pilot manifest and audit reports.
- [`scripts/pilot/`](scripts/pilot/) — sandbox and proof-checking prototype.
- [`paper/`](paper/) — research paper draft.
