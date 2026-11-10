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
with the original directory unchanged at that recovery checkpoint. Subsequent
user-authorized pruning of unrelated cached resources is disclosed below. It has no host grading report and is
recorded separately as `interrupted-needs-review`, not a completed model failure.
The last available native state is 10 turns started, 9 completed, Goal active;
final-turn usage remains incomplete. All 217 canonical completed-report checksum
lists and the preserved CompCert archive hash were also verified after recovery.
On 2026-11-11 (Asia/Shanghai), the user explicitly authorized resuming the study
after disclosure of low C: free space; this did not authorize cleanup or a WSL
restart. Resumption preflight `20261110T161455Z-bb263167c5dd` passed the read/write
filesystem and write/fsync checks, all 217 canonical report hashes, and
the frozen-source checks for 71 contexts and 472 files. C: had approximately
12.6 GB free at preflight; the largest historical native attempt occupied
160.7 MB. At 16:25 UTC on 2026-11-10 (2026-11-11 in Asia/Shanghai), exactly one
controller started a fresh Lean/off attempt for `P-e69f7e9ea72f14cf/lean`,
`20261110T162522Z-59d9b398b251`, using `gpt-6-luna`, medium reasoning and the
7200-second `attempt-entry-deadline-v1` budget. Startup establishes no model outcome.
Host diagnostics, partial costs and verified backup evidence are separate from
completed-run totals. Further distribution maintenance can interrupt unrelated
workloads and requires authorization.

At 16:29:55 UTC, `logind` reported `System is powering down`; an orderly shutdown
of the whole Ubuntu instance stopped the study, storage guard and agent. The
guard had not triggered, and the curator issued no shutdown, restart or stop
command. The initiator is not independently established; WSL session/instance
lifetime is the leading infrastructure hypothesis. The fresh off attempt's
completed result is retained, giving 217 canonical results (135 accepted,
68 rejected, 14 timeouts). The new on attempt `20261110T162707Z-07997fc15d4d`
has no host grade and is separately recorded as `interrupted-needs-review`,
not a completed model failure. Its 325 files (11,723,922 source bytes) were
archived to D: and every file hash verified; archive SHA-256 is
`164e794811479ac6faa68f45c6fcd6312d7c5ddcf3bb16fb758995e6f080cd22`.
The last observed native state was three turns started, two completed, one
client start, zero manual resumes and Goal active. The latest cumulative
provider snapshot records 252,693 input tokens (201,856 cached), 5,294 output
tokens (3,111 reasoning), and 257,987 total tokens; it supersedes the stale
232,736-token live snapshot. Final usage remains incomplete. The observed
cgroup peak was 317,825,024 bytes. Phase is `blocked-infrastructure-lifecycle`.
At the follow-up storage checkpoint C: had 7.18 GB free and Ubuntu's VHD occupied
683.52 GB. No new model attempt is planned while headroom remains poor. A
foreground WSL keeper passed seven isolated mocked tests and a 132.6-second
hidden Windows-client readiness probe: its Linux PID and boot ID persisted
without another curator WSL command during that interval. The probe started no
models and controlled no services; only its identified helper was ended after
verification. This mitigates the lifetime hypothesis without establishing the
shutdown initiator or restoring storage headroom. No subsequent model attempt
was started. Preserve the partial without repair or resumption; any eventual
retry requires a fresh attempt and current storage clearance. After the readiness
check the current phase is `blocked-infrastructure-storage`; no new on session
was started, and its completed new-revision off companion remains canonical.

At the user's request, the recurring monitor was deleted and unrelated retained
runtime resources were removed on 2026-11-10 at 18:19 and 18:25 UTC. Two independently
reviewed plans removed 76,262 files (13,899,455,060 content bytes): per-attempt
remote plugin catalogs, plugin/template caches and five non-proof system-skill
copies. Every removed file has a checksum-matched D: backup member; newer files
were separately archived and verified first. Exact removal manifests, original
metadata and backup-member pointers are retained privately. Original checksum
lists were not rewritten. Complete before/after hashes and metadata matched for
all retained files, including proofs, sessions, Goal databases, reports, checker
logs and usage records. The 217 canonical results and status hash are unchanged;
the CompCert probe and archive were untouched. The study directory's allocated
size fell from 18.03 GB to 3.79 GB. C: still had about 2.91 GB free: no VHD
compaction or distribution restart was performed, and the storage hold remains.
See the [cleanup audit](../benchmarks/construction/native-storage-cleanup-20261110.json).

A [minimal runtime configuration](../scripts/pilot/native_proof_runtime_minimal.toml)
now supplies future native attempts with apps, memories, plugins and the remote
plugin catalog disabled. The same installed
CLI, version 0.162.0, parsed it successfully in an isolated HOME/CODEX_HOME and
reported all four features disabled. This was a static configuration check;
no app-server or model was started and startup storage savings remain unmeasured.
Future reports snapshot the preset and policy sources and record runtime revision
`native-proof-runtime-minimal-v1`, the effective configuration hash and configured
feature values. Historical attempt configurations remain unchanged. After taking
the activity lock and before marking any job running, the controller refuses a
new attempt if C: free space is below 5 GiB or the retained study directory has
reached 8 GiB. The latter is an admission threshold between attempts, not a live
per-attempt disk quota; the existing external guard remains necessary during a
run. An unreadable storage measurement also stops admission.

The controller additionally checks the completed opposite-mode report's task,
platform, Goal mode, runtime revision and configuration hash. A missing legacy
runtime tag or any mismatch produces a separate runtime hold, without starting
an attempt, changing job/report status or automatically rerunning its companion.
Thus the completed new-wall-budget off report is retained; adopting the minimal
feature surface for its unfinished pair requires a separately reviewed runtime
transition. Existing complete pairs retain their original runtime cohort.
Forty-one isolated runtime-policy, protocol and deadline tests passed, including
controller hold scenarios; no model or real grader was run. Actual model-startup
storage savings remain unmeasured, and no new evaluation was started.

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
budget revision. The original reviewed [transition-plan snapshot](../benchmarks/construction/native-budget-transition-plan-20261110.json)
is preserved unchanged. After storage/requeue clearance, transition
`20261110T162125Z-c62c4ad93401` was applied once: it retained 108 complete legacy
pairs and selected only `P-e69f7e9ea72f14cf/lean` for fresh off/on sessions. Moving
its unmatched legacy off report to separately preserved protocol-superseded
evidence changed the canonical completed count from 217 to 216 (135 accepted,
67 rejected, 14 timeouts) at the transition. The original report
and its costs remain retained separately. This transition does not identify a
causal effect of changing the budget policy.

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

An external operational guard checks C: free space every five seconds against
a 5 GiB threshold. On a breach it freezes the verified controller and stops only
its descendant native agent/checker scopes. This best-effort guard never retries
or resumes an attempt; affected partials require infrastructure review and do
not count as completed model outcomes. It changes no prompt, grader or frozen
source. Seven isolated mock tests and independent review passed before startup.

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
