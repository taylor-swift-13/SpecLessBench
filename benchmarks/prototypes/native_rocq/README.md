# Native Rocq proof prototypes

These are representative proof attempts for the specification-free relational task. Each task supplies two implementations and a minimal domain/observation boundary, but no independent functional postcondition. Its solution must construct either an equality proof or a checked counterexample.

| File | Intended result | Status |
|---|---|---|
| `FactorialEquivalent.v` | Recursive factorial equals accumulator factorial | Checked by `coqc` and `coqchk` |
| `FactorialCounterexample.v` | Off-by-one accumulator mutant has a counterexample | Checked by `coqc` and `coqchk` |
| `ReverseEquivalent.v` | Direct recursive reverse equals accumulator reverse | Checked by `coqc` and `coqchk` |

The prototypes were checked with Coq 8.20.1 (`coqc` followed by `coqchk`). Run `make check` from this directory to repeat the check. This establishes the submitted Rocq propositions, not the correctness of any independent functional specification: no such specification is supplied. The next validation stage should add a matrix multiplication pair and a C/Clight pair; neither is represented as verified here yet.
