# Native Goal CompCert probe

The single-task probe finished at its four-hour limit on 2026-11-06, approximately
19:44--23:44 Asia/Shanghai. No other theorem or Goal-off control was launched.
Machine-readable evidence and artifact hashes are in [goal-probe-result.json](goal-probe-result.json).

| Setting or observation | Value |
| --- | --- |
| Task | `P-00e48e122a4702fd` (PackBits, CompCert) |
| Model | `gpt-6-luna`, medium reasoning |
| Native Goal | Confirmed active with `thread/goal/set` and `thread/goal/get` |
| Client-issued initial turns | 1 |
| Manual resumes | 0 |
| Native turns | 45 started, 44 completed; last turn interrupted |
| Completed tool commands | 1,067 |
| File-change events | 191 |
| Agent supervisor wall time | 14,400.002 seconds |
| Total attempt wall time | 14,408.550 seconds, including setup/cleanup |
| Agent cgroup peak | 3,221,237,760 bytes; configured limit 3 GiB |
| OOM events / kills | 94 / 81 |
| Final submission | 4,298 lines, no `solve` declaration |
| Outcome | timeout; no accepted proof |

The model continued inspecting semantics, editing proofs and invoking the compiler
through native Goal dispatch. It developed initialization, memory-relation,
input-store and execution-prefix lemmas. This establishes that native continuation
and sustained attempts occurred. It does not establish that the entire final
file or the requested equivalence theorem is proved. The complete safe,
terminating executions and observations were not connected to `solve`.

Repeated compiler OOM kills and proof errors materially limited progress. The
model sometimes described new results as compiled despite failing compiler logs;
those descriptions are not evidence of acceptance. The host stopped at the time
budget and did not run final grading beyond the exhausted budget. Checker and
axiom-audit fields therefore remain not-run, not passed.

Last reported session-cumulative tokens: 198,298,453 input, of which 196,388,480
cached, and 465,554 output. Cached input is a subset of input, not an additional
quantity. The native Goal counter was 2,375,527, matching uncached input plus
output for this observation; it must not be added to model usage. The interrupted
last turn may have unreported usage, so these are available reported counters,
not a guaranteed complete bill. Monetary cost and hosted inference memory are null.

Raw RPC send/receive events, configuration, goal lifecycle, reception timestamps,
the original submission, cgroup evidence and checksums remain in the private WSL
attempt directory named in the JSON summary. The initially loaded runner omitted
the timeout's native summary and labelled its stop `native-session-ended`.
Post-run metadata auditing reconstructed the counts and corrected this to
`time-budget`, preserving original metadata under `metadata-original/` and
recording hashes in `metadata-audit.json`. Raw events, proof, task and outcome
were not changed; no candidate proof was repaired or regraded.

This is one feasibility probe, not a paired effectiveness experiment. There is no
retained fresh Goal-off control, so no comparative success-rate or efficiency
claim is supported. CompCert evaluation is now suspended. The user authorized a separate Lean/Rocq Goal-on/off study; this failed CompCert probe is excluded from its results and costs.

The complete attempt was additionally archived after verifying all464regular files. Archive SHA-256: `bc905b6b1c1878fd60a6e1156aa3594d9ec6a5468ffd5169afcde77b4c7abb8b`. The original directory and per-file archive manifest remain private; no proof or event was changed.
