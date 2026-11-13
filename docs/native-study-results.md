# Native Lean/Rocq Goal study results

SpecLessBench completed all **276** planned GPT-6 Luna medium runs on
2026-11-13 at 17:02 UTC. The host accepted **163** submissions, rejected
**94**, and recorded **19** timeouts. Accepted submissions include 55
equivalence proofs and 108 checked concrete counterexamples.

| Platform | Goal | Runs | Accepted | Rejected | Timeout | Acceptance | Observed tokens | Recorded wall time |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Lean | Off | 69 | 22 | 47 | 0 | 31.9% | 6,082,541 | 1.41 h |
| Lean | On | 69 | 57 | 3 | 9 | 82.6% | 794,467,391 | 34.67 h |
| Rocq | Off | 69 | 28 | 41 | 0 | 40.6% | 9,862,804 | 1.71 h |
| Rocq | On | 69 | 56 | 3 | 10 | 81.2% | 1,332,379,944 | 40.18 h |

Across the 138 platform/context pairs, Goal-on accepted **113/138 (81.9%)**
and Goal-off accepted **50/138 (36.2%)**, a difference of **45.7 percentage
points**. The 69 contexts each appear on both platforms, so the pooled
denominator counts platform/context pairs.

| Platform | Both accepted | Only Goal-on accepted | Only Goal-off accepted | Neither accepted |
| --- | ---: | ---: | ---: | ---: |
| Lean | 22 | 35 | 0 | 12 |
| Rocq | 27 | 29 | 1 | 12 |
| Total | 49 | 64 | 1 | 24 |

The experiment compares a single ordinary turn with a native Goal that can
continue across turns. Both arms had a nominal 7,200-second limit and a
3 GiB agent sandbox. Each pair used the same frozen package, initial prompt,
model, effort, budget revision, and runtime revision. The host independently
checked submissions. Goal-on reported completion in 115 runs, of which the
host accepted 113 and rejected two.

The acceptance advantage came with substantially more work. Goal-on recorded
2,126,847,335 tokens and 74.86 summed attempt hours, compared with 15,945,345
tokens and 3.12 hours for Goal-off. Median recorded attempt time was 558.0 s
with Goal-on and 68.5 s with Goal-off. These are observed differences between
the two operating modes on this benchmark, with one canonical attempt per arm.

| Budget and runtime | Lean off → on | Rocq off → on |
| --- | ---: | ---: |
| Earlier clock and default runtime, 108 pairs | 18/51 → 44/51 | 26/57 → 47/57 |
| Attempt-entry clock and proof-only runtime, 30 pairs | 4/18 → 13/18 | 2/12 → 9/12 |

The earlier clock started after setup, and its reported wall times omit that
prefix. The later clock includes preparation, model work, and checking. The
14 earlier timeout reports record 7,205.85–7,217.18 s. The five later timeout
reports record 7,200.04–7,200.30 s, including post-decision finalization.
Cases entered the cohorts in queue order. The cohorts therefore differ in
case composition as well as clock and runtime. See the
[wall-budget audit](../benchmarks/construction/native-wall-budget-audit-20261110.json)
and [evaluation protocol](evaluation-batch.md).

The canonical reports sum to **280,713.034 s (77 h 58 min 33 s)** of measured
attempt time, including 275,263.830 s of agent work and 3,021.899 s of host
checking. They record **2,142,792,680 observed tokens**, comprising
2,132,988,747 input (2,098,973,696 cached) and 9,803,933 output (5,812,643
reasoning). Cached and reasoning counts are subsets. All 276 reports contain
a last cumulative usage snapshot. The 19 timeout snapshots are incomplete.
Billing and hosted-model memory are unknown. The largest recorded agent and
checker cgroup peaks were 3,221,229,568 and 2,740,830,208 bytes, respectively.
Two agent peaks and 72 checker peaks were unrecorded.

The ledger tracks 286 distinct Luna attempts. In addition to the 276
canonical attempts, it retains four ungraded interruptions, four
infrastructure failures, and two reports superseded by protocol migration.
Six of the eight interrupted or failed attempts have last-observed cumulative
usage totaling 100,775,296 tokens, all incomplete. The two authentication
failures have no recorded usage. The four finalized infrastructure reports
record 6,354.695 s of attempt time, and the four ungraded interruptions record
10,327.667 s of observed agent time. The two superseded reports record
164,092 tokens and 260.874 s. These costs are excluded from the table.

A retrospective Lean audit reviewed 102 reports and rechecked 14 audit
rejections. Eleven became accepted. The canonical ledger counts each
adjudicated attempt once using its original model resources. Rechecking took
222.726 host checker seconds and made no model calls. See the
[Lean audit correction](../benchmarks/construction/native-audit-correction-20261110.json).

The separately authorized Sol Lean equivalence attempt passed. The Sol MST
specification comparison recorded eight accepted submissions, one audit
rejection, and one infrastructure interruption. Its nine host reports
recorded 30,874,428 tokens and 13,478.556 s. The independent Sol equivalence
attempt, Sol specification cases, CompCert probe, and curator conversation
are outside the Luna totals.

The [machine-readable results](native-study-progress.json) record condition,
pair, cohort, and cost totals and the SHA-256 of the final batch status.
Validation checked 8,592 entries across 842 canonical and original
adjudicated-attempt manifests. Raw submissions and attempt records are
retained in the private study directory.
