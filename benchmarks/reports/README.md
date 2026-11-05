# Reference reports

Each evaluation report is stored separately by task, platform, theorem branch, and run ID. Reports contain proof attempts and answers. The entire factorial family is reserved as public reference material and excluded from the evaluation set on all three platforms; see the [evaluation policy](../pilot-v1/evaluation-policy.json).

The existing reference is [the Lean factorial equivalence run](P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5/report.md). Its source-rebuilt goal, binding to the frozen theorem, proof, and allowed axiom dependencies have been checked by Lean; it is a gold-standard proof reference for this theorem under the stated axiom policy. This is one theorem, not a benchmark-wide evaluation; unproved branches remain pending.

| Factorial reference theorem | Lean | Rocq | CompCert |
| --- | --- | --- | --- |
| Recursive / accumulator equivalence | [Proved](P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5/report.md) | Pending | Pending |
| Reference / mutant counterexample | [Proved](P-a80b8283427dcbd7/lean/counterexample/20261105T152523Z-ff7f7147b74b/report.md) | Pending | Pending |

All six instances are excluded from evaluation regardless of proof status. The Lean counterexample package uses a fixed witness; it is intended as a certificate example, not as evidence that an agent discovered the witness.

Each run includes the task snapshot, prompt, Codex configuration, observed CLI model catalog, toolchain fingerprint, model and tool events, event receipt times, proof, checker output, resource measurements, machine-readable report, and checksums. Codex was configured to use `gpt-6-luna` with `medium` reasoning, and the CLI catalog included both. This is the recorded model configuration for the run; the service did not provide an independently verifiable server-side model version. Hidden model reasoning, hosted-model memory, and actual billing are unavailable. The OS, system libraries, and model backend are not locked.

The report records the raw and Windows-normalized Git status at run start and SHA-256 hashes for the critical scorer and task files. Both status checks were clean and all critical file hashes matched the recorded commit. The older public example was removed from the current tree at the user's request, but its proof remains accessible through existing Git history.

To verify file integrity and replay the proof on the original WSL toolchain:

```bash
REPORT=benchmarks/reports/P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5
python3 scripts/pilot/verify_reference.py "$REPORT"
```

Replay requires the configured Lean 4.34.0 toolchain, bubblewrap, and a working user-level systemd cgroup. The command checks file hashes, timestamps and event usage, fingerprints the Lean toolchain, rebuilds the task from source, audits the binding lemmas against the named frozen target, and rechecks the proof and its axioms. It does not verify the model's identity or reconstruct hidden model reasoning.
