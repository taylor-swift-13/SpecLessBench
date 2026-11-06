# Sequential evaluation

All historical model evaluation and reference-run artifacts were deleted at the user's request on 2026-11-06, including previously accepted results. The batch is paused
for prompt review; all 207 eligible platform instances are pending. No retained
proof result will be skipped or counted in the next study. The paused monitor must
not restart the worker until the user authorizes the reviewed protocol.

The Chinese review draft is [evaluation-protocol.zh-CN.md](evaluation-protocol.zh-CN.md).
The provisional configuration remains gpt-6-luna medium, strictly serial, with ten
total rounds (initial plus nine same-session resumes), a shared 7200-second budget
for Lean/Rocq and 14400 seconds for CompCert, including checking. It is not running.

Certified source-bound packaging currently covers 141 of 207 instances; the other
66 remain unprepared. Task sources, frozen goals, package bindings, differential
tests and construction cost records are preserved. Factorial remains outside the
evaluation split; its historical reference-run artifacts were also deleted.

Each agent sees only one read-only task package and its own writable workspace.
It chooses either equivalence or a literal counterexample; no expected label or
witness is given. The host independently constructs the selected obligation,
checks the submitted proof, and audits axiom dependencies. Counterexamples must
prove validity, both executions and distinct observations. Existing gold proofs
and their checker dependencies are unchanged.

Native Rocq submissions are independently checked by `coqchk` and must have no
axiom dependencies. The Lean prompt is unchanged from the first batch; early
submissions with missing claims or an incorrect theorem name remain rejected
and are never silently repaired or overwritten.

Clight packages retain the frozen execution semantics, safety and termination
requirements, and full 8192-word output observations. Their C sources match the
frozen preprocessed build hashes. AST modules have neutral names; unused build
metadata is omitted. Rocq checks correspondence of both selected goals to the
frozen targets under module rebinding. Counterexample claims provide output
prefixes including their length slot; the trusted renderer pads them to 8192
words and pairs each with main return zero. CompCert assumptions follow the
existing grader allowlist; candidate axioms, including namespace spoofing, fail.

Private artifacts are on WSL's Linux filesystem:

```text
~/.local/share/speclessbench/batches/luna-medium/status.json
~/.local/share/speclessbench/batches/luna-medium/history.jsonl
~/.local/share/speclessbench/runs/evaluation/<task>/<platform>/attempts/<run-id>/
```

Each attempt contains the prompt, model/agent/sandbox configuration, CLI model
catalog observation, source/package/toolchain fingerprints, live JSON conversation
and tool events, event reception timestamps, agent stderr, submitted claim and
proof, checker logs, resources, a JSON/Markdown report and artifact checksums.
`live.json` updates every five seconds while the agent runs. The full private
workspace is retained. This records all CLI-emitted information; hidden model
reasoning and data omitted by the CLI cannot be recovered. Billing and hosted
inference memory remain null. Cached input tokens are part of input tokens and
must not be added to them again.

New preparation and obligation builds also retain `compile-costs.jsonl`: command,
exit status, wall/CPU time and GNU time's process maximum RSS. This RSS measure
is separate from the agent/checker cgroup peaks. Earlier unmeasured stages are
not backfilled with estimates. Failed preparation sources, compiler diagnostics
and issue records remain in private package directories, outside agent mounts.

`record_curator_usage.py` separately captures this desktop chat's actual
`token_usage_record` entries and model contexts, checks that request sums equal
the app's thread counter, and preserves compressed evidence privately. Its
public `benchmarks/construction/curator-workflow-usage.json` covers the entire
curator workflow, including discussion and monitoring. It overlaps historical
construction snapshots, excludes separately launched reference/evaluation workers, and is not a
construction-only or per-family bill. Never sum it with the old construction
ledger without deduplicating the overlapping request windows. Unavailable
model attribution, inference memory and billing remain null.
The historical construction summarizer includes only explicitly tagged
prototype jobs when reading the shared pilot-job memory log, so downstream
evaluation/reference checking cannot silently inflate that construction view.

Systemd does not inherit interactive-shell proxies automatically. A future launch
must pass configured proxy variables explicitly.

Inspect progress without starting another worker:

```bash
cat ~/.local/share/speclessbench/batches/luna-medium/status.json
journalctl --user -u specless-luna-batch -n 30 --no-pager
systemctl --user status specless-luna-batch --no-pager
```

When re-enabled by the user, the chat heartbeat checks every ten minutes and continues preparing pending
packages when the worker is idle. It reports meaningful milestones, actionable
failures and completion; unchanged state stays quiet. No finite completion time
is promised until every instance has a certified adapter. Ten rounds is a maximum, not a requirement to keep an already accepted proof running.
