# Reference reports

Each evaluation report is stored separately by task, platform, theorem branch, and run ID. Reports contain proof attempts and answers. The entire factorial family is reserved as public reference material and excluded from the evaluation set on all three platforms; see the [evaluation policy](../pilot/evaluation-policy.json).

Each new local run has its own directory under `~/.local/share/speclessbench/runs/reference/<task>/<platform>/<claim>/<run-id>/` for reference work, or `~/.local/share/speclessbench/runs/evaluation/<task>/<platform>/<claim>/<run-id>/` for formal evaluations. Failed or timed-out attempts are kept separately too. This repository directory is for reference reports only; publishing a reference attempt does not overwrite another attempt or the frozen reference.

The frozen factorial reference contains six independently checked theorem reports, listed below. Their status applies to the factorial family and does not imply benchmark-wide proof coverage. The [reference manifest](factorial-reference.json) pins the report checksums and the frozen pilot snapshot.

| Factorial reference theorem | Lean | Rocq | CompCert |
| --- | --- | --- | --- |
| Recursive / accumulator equivalence | [Proved](P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5/report.md) | [Proved](P-dbec465c356ed73d/rocq/equivalence/20261105T154526Z-514a9df0dc21/report.md) | [Proved under the listed trusted-library assumptions](P-dbec465c356ed73d/compcert/equivalence/20261105T162658Z-672a823421d0/report.md) |
| Reference / mutant counterexample | [Proved](P-a80b8283427dcbd7/lean/counterexample/20261105T152523Z-ff7f7147b74b/report.md) | [Proved](P-a80b8283427dcbd7/rocq/counterexample/20261105T154425Z-e4b4242a737b/report.md) | [Proved under the listed trusted-library assumptions](P-a80b8283427dcbd7/compcert/counterexample/20261105T154959Z-97a1e5a4283a/report.md) |

All six instances are excluded from evaluation regardless of proof status. The Lean counterexample package uses a fixed witness; it is intended as a certificate example, not as evidence that an agent discovered the witness.

The earlier Rocq projected-goal runs are retained alongside the final original-goal runs for construction-cost accounting. Their reports explicitly mark the original theorem as unchecked in those runs.

Each run includes its task snapshot, prompt, Codex configuration, model and tool events, event receipt times, proof, checker output, resource measurements, machine-readable report, and checksums. The Lean runs use the configured `gpt-6-luna` model with `medium` reasoning; the Rocq runs use `gpt-6.1-sol` with `medium` reasoning. These are recorded client configurations; the service did not provide an independently verifiable server-side model version. Hidden model reasoning, hosted-model memory, and actual billing are unavailable. The OS, system libraries, and model backend are not locked. The Lean runs also record the observed CLI model catalog and a toolchain fingerprint.

The Lean reports record Git status and SHA-256 hashes for critical scorer and task files. The Rocq verifier checks the frozen source hashes and rebuilds the original target before rechecking the proof.

To verify file integrity and replay the proof on the original WSL toolchain:

```bash
REPORT=benchmarks/reports/P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5
python3 scripts/pilot/verify_reference.py "$REPORT"
```

Replay requires the configured Lean 4.34.0 toolchain, bubblewrap, and a working user-level systemd cgroup. The command checks file hashes, timestamps and event usage, fingerprints the Lean toolchain, rebuilds the task from source, audits the binding lemmas against the named frozen target, and rechecks the proof and its axioms. It does not verify the model's identity or reconstruct hidden model reasoning.

To replay a Rocq reference with the configured Rocq 8.20.1 toolchain and the same isolation prerequisites:

```bash
REPORT=benchmarks/reports/P-a80b8283427dcbd7/rocq/counterexample/20261105T154425Z-e4b4242a737b
python3 scripts/pilot/verify_factorial_rocq_original.py "$REPORT"
```

The Rocq checker rebuilds the original source modules and exact theorem target, checks the submitted proof with `coqchk`, and rejects non-closed assumptions.

For the CompCert counterexample, use `python3 scripts/pilot/verify_factorial_compcert_original.py REPORT`. This rebuilds the frozen Clight AST and semantics, checks the bridge to the original theorem with `coqchk -bytecode-compiler yes`, and audits assumptions against the CompCert namespace and named Rocq library dependencies. The bytecode conversion engine is part of the trusted checking setup. The run was initially rejected by the previous zero-assumption policy; its original verdict is preserved alongside the subsequent verification.

The same verifier checks the CompCert equivalence report. Its default per-check limit is 600 seconds; the generic sealed grader's 90-second default timed out on the equivalence proof even though the longer check passed. The frozen factorial implementation uses the shared 8,192-word output buffer; its initialization and observation are part of the checked task. Their effect on proof and checking cost can be measured separately. Any changed implementation or goal requires independently regenerated artifacts and proof checks.
