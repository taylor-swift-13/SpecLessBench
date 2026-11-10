# Native Lean/Rocq Goal study

The current study runs `gpt-6-luna`, medium reasoning, over Lean and Rocq only.
CompCert evaluation is suspended. Its four-hour failed probe is preserved in its
original directory and a separately verified full archive; see [the result](goal-probe.md).
It is excluded from the native study's counts and costs.

Operational checkpoint, 2026-11-10 09:35 UTC: Windows removed Ubuntu's virtual
disk after a write failed with `STATUS_DISK_FULL`. WSL subsequently reported
I/O errors and emergency read-only state. The last confirmed checkpoint had
217 terminal runs (135 accepted, 68 rejected, 14 timeouts). At 09:43 UTC a new
WSL VM booted and re-exposed the disk; the initiator is unknown. The curator did
not issue a termination or restart command. The interrupted Lean/on attempt was
inspected after recovery: 432 files were archived and every file hash verified,
with the original directory unchanged. It has no host grading report and is
recorded separately as `interrupted-needs-review`, not a completed model failure.
The last available native state is 10 turns started, 9 completed, Goal active;
final-turn usage remains incomplete. All 217 canonical completed-report checksum
lists and the preserved CompCert archive hash were also verified after recovery.
The service remains stopped pending storage recovery preflight and the timing
correction below. Host diagnostics, partial costs and verified backup evidence
are separate from completed-run totals. Further distribution maintenance can
interrupt unrelated workloads and requires authorization.

The frozen evaluation selection contains 69 contexts (factorial excluded), each
on Lean and Rocq. Each theorem/platform runs once with Goal off and once with
Goal on: **276 independent runs**. Order is deterministic: context, Lean then
Rocq, off then on. The initial task prompt and platform interface are identical
within each pair. Workspaces and sessions are fresh and isolated for every run;
no proofs or outcomes are shared. Only native Goal mode differs.

At the budget-revision boundary, every incomplete pair whose completed companion
used the legacy clock is restarted in fresh off/on sessions, regardless of that
companion's result. Its original report and costs remain separately visible as
protocol-superseded evidence. Complete legacy pairs are retained and reported by
budget revision. The reviewed [transition plan](../benchmarks/construction/native-budget-transition-plan-20261110.json)
currently selects one Lean pair and retains 108 complete pairs; applying it would
change the canonical completed count from 217 to 216 before fresh off/on runs.
It has not been applied and requires separate storage/requeue clearance. This
transition does not identify a causal effect of changing the budget policy.

The requested protocol has a shared 7200-second wall limit including setup,
model work and checking, a 3 GiB sandbox and no token budget. A dated timing
audit found that the first 217 completed reports used a clock starting after
setup; their reported total wall time also omits an earlier entry prefix.
None of the 135 accepted or 68 rejected reports records total wall time above
7200 seconds. The 14 timeout reports record 7205.85--7217.18 seconds, including
termination/finalization overhead. These observations do not establish strict
setup-inclusive conformance or counterfactual scores. Original reports, results
and model costs remain unchanged; see the [timing audit](../benchmarks/construction/native-wall-budget-audit-20261110.json).
Prospective revision `attempt-entry-deadline-v1` uses one deadline from run entry
through agent and checking processes, disallows late acceptance, and reports
termination/finalization overhead separately. Expiration before agent launch is
infrastructure failure requiring inspection. The initial prompts remain unchanged.
Goal-off starts one ordinary turn. Goal-on
sets and verifies a real persisted Goal and permits its native automatic turns.
The client issues exactly one `turn/start` in either condition. There is no
external retry/resume loop or ten-round cap. After a native Goal stays idle for
120 seconds without continuing, it is recorded as `native-continuation-not-observed`;
this is distinguished from timeout, blocked, complete and accepted.

The single controller is `scripts/pilot/batch_native_evaluation.py`, launched as
`specless-native-study.service`. Global controller and preparation/activity locks
serialize complete attempts including setup and grading. Never launch two workers.
Infrastructure errors or interrupted attempts stop for inspection; any actual
retry needs a new attempt ID and must retain the previous partial evidence.

State and artifacts on the private WSL filesystem:

```text
~/.local/share/speclessbench/batches/native-luna-medium/status.json
~/.local/share/speclessbench/batches/native-luna-medium/history.jsonl
~/.local/share/speclessbench/runs/evaluation/<task>/<platform>/goal-<off|on>/attempts/<id>/
```

The status contains separate `by_condition` counts and costs for `lean/off`,
`lean/on`, `rocq/off`, `rocq/on`. No prior results are reused. Currently 109 of
138 native platform packages are certified (52 Lean,57 Rocq), supporting218runs;
29 packages/58runs await preparation. Unprepared items are pending, not failures.
Prepare only native packages while no evaluation or checker is running, retain
frozen implementations/domains/observations/targets and certify source binding
before making them eligible. Do not start CompCert or expose other tasks/labels.
For isolated record types, correspondence may use an explicit representation
map and constructive two-way proofs for both frozen branches. The Rocq evaluator, tokenizer,
frame-stream, LRU, lease-table and transaction adapters check this transport without adding functional extensionality
or axioms. Lean record transport uses only Lean's permitted standard axioms.

Each attempt preserves config/model/catalog observations, exact prompt/components
and hashes, native Goal objective and API confirmation, all available RPC requests,
responses and notifications with timestamps, original work/submission/claim,
deterministic target/axiom audits and checker logs, token/time/cgroup data and
checksums. Runner sources are snapshotted and hashed. Native lifecycle counts and
last observed Goal state survive timeouts; a Goal self-report is never acceptance.
Lean allows its documented three standard axioms. Under scoring revision
`lean-native-kernel-replay-v1`, closed native-decide facts can also be independently
discharged by kernel checking; their names alone never justify acceptance.
Native Rocq requires a closed proof and independent coqchk. Candidate placeholders,
undischarged axioms and changed goals fail. The dated [native computation
adjudication](native-computation-audit.md) preserves original reports, revised
decisions and separate post-hoc checking costs without rerunning model attempts.

Use the last reported cumulative model-usage snapshot, never sum native-turn
snapshots. Cached input is part of input; reasoning output is part of output.
Interrupted final-turn usage may be incomplete and is marked as such. Goal's own
usage counter is separate and not added again. Peak memory is a maximum, not a
sum. Billing and hosted inference memory remain null. The curator whole-chat
metering overlaps construction snapshots and must not be summed with them or
reported as construction-only/per-family cost.

Inspect the status and `journalctl --user -u specless-native-study`; do not launch
another controller to inspect progress. The monitor checks live processes first,
stays quiet on ordinary progress, and reports milestones, actionable failures or
completion. When all276runs are terminal, summarize results/costs and stop monitoring.
