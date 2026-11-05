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
for the worker. The initial adapter covers native Lean reversal and sum pairs.
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
