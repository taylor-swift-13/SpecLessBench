# Sequential Luna evaluation

Evaluation and monitoring resumed on 2026-11-06 at the user's request.
The serial worker uses the same-session continuation policy below.

The strengthened prompt adds an explicit completion checklist: save both required
artifacts, compile the final exact theorem, fix errors before ending, and await
independent target/axiom checking. It states the actual shared budget and total
round cap. The worker was restarted with this prompt on 2026-11-06 after retaining
33 accepted attempts (31 legacy and two continuation successes). The interrupted
CompCert attempt was deleted at the user's request; known aggregate costs are
recorded separately, with incomplete-round costs explicitly unknown. Each attempt's stored
prompt and runner fingerprint identify its actual protocol. Do not relabel old
attempts as having received the revised checklist.

New runs use `gpt-6-luna`, medium reasoning, one theorem at a time and a
3 GiB sandbox. Lean/Rocq have a shared two-hour budget; Clight has four hours.
The budget covers all resumed agent rounds and deterministic checking, starting
after setup. At most ten rounds are allowed: the initial run and nine resumes.
The controller records the original session ID and uses `codex exec resume ID`;
it never substitutes a new session. A failed check is fed back to that session.
Acceptance, budget exhaustion or the round limit stops the attempt. Infrastructure
failures stop for review. Checker stages retain a 600-second cap, reduced to fit
the remaining attempt budget.

Old runs used ephemeral sessions, so failed historical runs cannot be resumed.
At the user's request, 110 rejected attempts and one infrastructure attempt were
deleted. All 31 accepted attempts remain, migrated to `rounds/000` with original
reports/configurations preserved under `legacy/`. Their actual old 3,600-second
configuration is unchanged and they are labelled `legacy-one-shot`; they are
not evidence for the new continuation policy. They will be skipped on rerun.
At the updated-prompt restart, 174 instances remained: 108 certified and 66 unprepared.
Factorial remains reference-only and excluded from the 207-instance evaluation.

After the user explicitly resumes, launch the same serial worker with the
existing proxy environment and pass `--resume` to `batch_evaluation.py`.
Without that flag, a paused batch exits without launching an agent.

Only packages with checked correspondence to the frozen sources are eligible
for the worker. Certified coverage is 141 of 207 instances: 41 Lean, 43 Rocq
and 57 Clight packages. This includes algorithmic, codec, graph, data-structure,
path and systems/numerical pairs. Two Lean component packages remain pending.
Fourteen Clight-only contexts cover tagged evaluation, quoted tokenization,
streaming frames, nested transactions, LRU, leases and counting sort; their
native packages remain pending. Clight input predicates can be projected
directly from their frozen word-vector domains, with kernel checking against
both original goals, independently of native packaging. Frozen observations
retain ordering/tie semantics, error details, traces and full C output buffers.
Other instances wait for adapters; they are not counted as model failures.
Adding a certified package lets the same serial worker pick it up. Preparation
must wait until no theorem is running. An exclusive worker lock prevents two
controllers. An interrupted attempt requires review before another attempt.
Infrastructure errors stop the batch for inspection.

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

Systemd does not inherit interactive-shell proxies automatically. The launch
command passes the configured proxy variables explicitly. An initial attempt
without them failed model routing; its raw events and partial report remain
separate from the corrected retry, with unavailable usage/memory fields null.

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
