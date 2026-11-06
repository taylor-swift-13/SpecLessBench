# Goal-mode evaluation pilot

The previous model-run results and baseline batch were deleted at the user's
request. The ten-round external resume policy is retired. Do not launch the old
batch controller. The full benchmark is not running.

The user requested first testing ONE CompCert theorem with native Goal:
`P-00e48e122a4702fd`, gpt-6-luna medium, 14400-second shared wall budget and a
3 GiB isolated sandbox. The service was `specless-goal-probe.service`; it is now inactive after the four-hour timeout. See [the audited probe result](goal-probe.md). No full batch or Goal-off run was launched.

`goal_client.py` uses the installed Codex app-server's real `thread/goal/set`
and `thread/goal/get` APIs. It sends exactly one client `turn/start`; later turns
are native Goal continuations, not manual resumes. Raw requests, responses,
notifications, lifecycle state and cumulative usage are preserved in events.jsonl.
The goal must be confirmed active before inference. A plain `/goal` text prompt
is not used as a substitute. Any unsupported API or unexpected permission request
is an infrastructure error, not a model proof failure.

For a future same-model Goal-on/off comparison, both conditions use the same
baseline task prompt, interface, tools, frozen target and time limit. Goal-off
runs one normal turn; Goal-on enables the persisted native objective and allows
its native continuations. There is no external ten-round cap or rejection-feedback
resume loop. The host grades the original final submission with the same sealed
grader. Native Goal completion is recorded separately and never counts as proof
acceptance by itself. The current probe supports CompCert only; other platforms
and the full comparison are not yet launched.

If the native goal stays active but no continuation begins for 120 seconds after
a completed turn, the probe records `native-continuation-not-observed`. This
bounds an idle infrastructure probe; it is not an assertion that the theorem is
unprovable. Goal blocked/complete statuses and timeout are recorded distinctly.
The raw stream must establish actual tool activity and source changes before
claiming sustained proof work.

Native probe artifacts:
`~/.local/share/speclessbench/runs/evaluation/<task>/compcert/goal-on/attempts/<id>/`.
Read live.json, events.jsonl, per-attempt configuration and final report. Only one
probe may run; do not prepare task packages or launch another theorem concurrently.
The remaining 207-instance study awaits user direction after this probe.
All frozen sources, differential tests, source-bound packages and construction
cost records remain intact; factorial stays excluded from the evaluation split.

Token accounting uses the last session-cumulative usage snapshot, never the sum
of snapshots. Timing and cgroup peaks include local app-server/client/tool work,
not hosted inference memory. Billing and hosted memory remain unknown. The
curator whole-chat usage series is separate and overlaps construction snapshots;
never sum it with those snapshots or call it construction-only/per-family cost.
