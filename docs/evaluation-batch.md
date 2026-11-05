# Sequential Luna evaluation

This batch uses `gpt-6-luna`, medium reasoning, one theorem attempt at a time,
a 3 GiB agent cgroup and a 3,600-second agent timeout. Checker stages have a
separate 600-second limit. The entire factorial family remains reference-only.
The evaluation manifest contains 69 contexts / 207 platform instances.

Run from the repository in the existing WSL environment:

```bash
python3 scripts/pilot/prepare_evaluation.py
systemd-run --user --unit=specless-luna-batch --working-directory="$PWD" \
  --setenv="HTTP_PROXY=$HTTP_PROXY" --setenv="HTTPS_PROXY=$HTTPS_PROXY" \
  --setenv="NO_PROXY=$NO_PROXY" --setenv="http_proxy=$http_proxy" \
  --setenv="https_proxy=$https_proxy" --setenv="no_proxy=$no_proxy" \
  /usr/bin/python3 -u "$PWD/scripts/pilot/batch_evaluation.py"
```

Only packages with checked correspondence to the frozen sources are eligible
for the worker. The initial adapters cover reversal, sum, matrix multiplication,
naive matching/KMP and queue pairs on all three platforms: 30 eligible instances.
Prim/Kruskal forest comparisons and stable record sorting add five contexts
on all three platforms. Two block/stream Base64 contexts add another six
instances. Six Floyd/Dijkstra, Tarjan/Kosaraju and naive/Boyer–Moore contexts
add 12 Rocq/Clight instances, bringing certified coverage to 63 instances;
their Lean packages remain pending. Frozen observations compare distance
matrices, pairwise component membership and first-match positions. Tie/edge-mask,
payload-order and exact encoded-byte observations retain their frozen domains.
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

The chat heartbeat checks every ten minutes and continues preparing pending
packages when the worker is idle. It reports meaningful milestones, actionable
failures and completion; unchanged state stays quiet. No finite completion time
is promised until every instance has a certified adapter. Model time alone is
bounded by 207 hours at the current timeout, excluding preparation/checking.
