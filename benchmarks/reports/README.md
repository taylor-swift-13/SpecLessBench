# Reference reports

Each evaluation report is stored separately by task, platform, theorem branch, and run ID. Reports contain proof attempts and answers: **published reference tasks are not suitable as blind evaluation items**.

The current reference is [the Lean factorial equivalence run](P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5/report.md). It is one integration run, not a benchmark-wide evaluation. Other tasks and branches are not yet connected to the scorer; no reports are claimed for them.

Each run includes the task snapshot, prompt, Codex configuration, observed CLI model catalog, toolchain fingerprint, model and tool events, event receipt times, proof, checker output, resource measurements, machine-readable report, and checksums. The model catalog confirms that the requested identifier and reasoning setting appeared in the CLI catalog; it does not independently attest the model that served a particular response. Hidden model reasoning, hosted-model memory, actual billing, and independently confirmed server-side model identity are unavailable. The OS, system libraries, and model backend are not locked.

The report records the raw and Windows-normalized Git status at run start and SHA-256 hashes for the critical scorer and task files. Both status checks were clean and all critical file hashes matched the recorded commit. The older public example was removed from the current tree at the user's request, but its proof remains accessible through existing Git history.

To verify file integrity and replay the proof on the original WSL toolchain:

```bash
REPORT=benchmarks/reports/P-dbec465c356ed73d/lean/equivalence/20261105T145347Z-3b3c245438c5
python3 scripts/pilot/verify_reference.py "$REPORT"
```

Replay requires the configured Lean 4.34.0 toolchain, bubblewrap, and a working user-level systemd cgroup. The command checks file hashes, timestamps and event usage, fingerprints the Lean toolchain, rebuilds the task from source, audits the binding lemmas against the named frozen target, and rechecks the proof and its axioms. It does not verify the model's identity or reconstruct hidden model reasoning.
