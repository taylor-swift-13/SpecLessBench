# Reference reports

Each evaluation report is stored separately by task, platform, theorem branch, and run ID. Reports contain proof attempts and answers: **published reference tasks are not suitable as blind evaluation items**.

The first reference is [the Lean factorial equivalence run](P-dbec465c356ed73d/lean/equivalence/20261105T135151Z-e24f4e321faf/report.md). It is one integration run, not a benchmark-wide evaluation. Other tasks and branches are not yet connected to the scorer; no reports are claimed for them.

Each run includes the task snapshot, prompt, Codex configuration, model and tool events, event receipt times, proof, checker output, resource measurements, machine-readable report, and checksums. Run artifacts retain only the information supplied by the tool and platform. In particular, hidden model reasoning, hosted-model memory, actual billing, and independently confirmed server-side model identity are unavailable.

The report records `tracked_files_dirty_at_start: true`. A later check identified Windows/WSL line-ending differences in tracked bookkeeping files; the frozen task files and evaluator audit were verified independently. This later observation does not establish the exact contents of every modified file at run start.

To verify file integrity and replay the proof on the original WSL toolchain:

```bash
REPORT=benchmarks/reports/P-dbec465c356ed73d/lean/equivalence/20261105T135151Z-e24f4e321faf
python3 scripts/pilot/verify_reference.py "$REPORT"
```

Replay requires the configured Lean 4.34.0 toolchain, bubblewrap, and a working user-level systemd cgroup. The command checks archive and event integrity and runs the proof checker, including its axiom policy; it does not verify the model's identity or reconstruct hidden model reasoning.
