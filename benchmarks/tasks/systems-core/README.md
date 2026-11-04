# Graph, state and numerical executable references

Five groups supply ten contexts and thirty Lean, Rocq and C/CompCert instances. Graph closure, banded alignment and fixed-point resampling exercise three different computation patterns. Scoped lookup and renewal retain two interface-oriented comparisons. See [task domains and exact targets](TASKS.md) and [fixture origins and adaptations](fixtures.json).

The C implementations use fixed storage and closed helper calls. The normalized Clight AST audit records four or five direct-call edges from main along the longest chain. These counts describe source structure. The preliminary difficulty labels in [the group registry](groups.json) are hypotheses about the relations solvers may need.

Reproduction uses the existing pinned WSL toolchain.

```sh
python3 scripts/construction/systems_action.py scripts/construction/prepare_systems.py
python3 scripts/construction/build_systems.py
python3 scripts/construction/run_systems.py --smoke
python3 scripts/construction/run_systems.py
python3 scripts/construction/systems_action.py scripts/construction/audit_systems_calls.py
python3 scripts/construction/prepare_systems_targets.py
python3 scripts/construction/check_systems_contract.py
python3 scripts/construction/finalize_systems.py
```

Preparation is a curator action. The differential driver records source-derived, boundary, exhaustive, structured and random inputs separately where applicable. Each unique input has nine behavior evaluations across three variants and three platforms. The driver additionally checks Lean and Rocq input predicates and measures the envelopes of whole runs. Selected successful corpora count toward coverage. All attempts, including failures, remain in the cost records.

Compiler and audit commands record wall time, CPU time and maximum single-process RSS. Shared authoring tokens are recorded once in the batch usage snapshot. The group records leave exact per-group token attribution, concurrent process-tree peak and hosted memory unset.
