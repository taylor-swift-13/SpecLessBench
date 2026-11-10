# Native Lean/Rocq Goal study

The current study runs `gpt-6-luna`, medium reasoning, over Lean and Rocq only.
CompCert evaluation is suspended. Its four-hour failed probe is preserved in its
original directory and a separately verified full archive; see [the result](goal-probe.md).
It is excluded from the native study's counts and costs.

The frozen evaluation selection contains 69 contexts (factorial excluded), each
on Lean and Rocq. Each theorem/platform runs once with Goal off and once with
Goal on: **276 independent runs**. Order is deterministic: context, Lean then
Rocq, off then on. The initial task prompt and platform interface are identical
within each pair. Workspaces and sessions are fresh and isolated for every run;
no proofs or outcomes are shared. Only native Goal mode differs.

Each run has a shared 7200-second wall limit including model work and checking,
a 3 GiB sandbox and no token budget. Goal-off starts one ordinary turn. Goal-on
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
`lean/on`, `rocq/off`, `rocq/on`. No prior results are reused. Currently 105 of
138 native platform packages are certified (51 Lean,54 Rocq), supporting210runs;
33 packages/66runs await preparation. Unprepared items are pending, not failures.
Prepare only native packages while no evaluation or checker is running, retain
frozen implementations/domains/observations/targets and certify source binding
before making them eligible. Do not start CompCert or expose other tasks/labels.
For isolated record types, correspondence may use an explicit representation
map and constructive two-way proofs for both frozen branches. The Rocq evaluator, tokenizer,
frame-stream, LRU and transaction adapters check this transport without adding functional extensionality
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
