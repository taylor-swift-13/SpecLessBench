# Lean native computation adjudication

The curator requested this scoring correction on 2026-11-10 after inspecting
Lean submissions rejected solely for `native_decide` dependencies. It changes
host adjudication, not model submissions, frozen task definitions, literal
claims, initial prompts or native Goal execution.

The previous auditor accepted only `propext`, `Classical.choice` and `Quot.sound`.
Lean 4.34 implements `native_decide` by compiling a closed Boolean decision
procedure and recording its successful evaluation as a generated axiom. A
submission using that official tactic could therefore compile and pass the
fixed-goal gate, yet fail the dependency audit. Such a rejection establishes a
trust-policy mismatch, not that the submitted counterexample is false. The
[Lean manual](https://lean-lang.org/doc/reference/latest/Axioms) documents this
extra dependency and compiler trust boundary.

## Corrected rule

Policy `lean-native-kernel-replay-v1` retains the protected exact-goal gate and
imports compiled artifacts at trust level zero with candidate environment
extensions disabled. The auditor traverses actual checked declarations rather
than trusting candidate-provided dependency summaries.

The three standard axioms remain allowed. An additional Submission-owned axiom
with the ordinary `native_decide` shape is eligible for discharge only when its
type is a closed `Eq Bool (decide P inst) true`. The auditor independently checks
the expression's type and reduces it to `true` using Lean's kernel. It does not
execute candidate native code, `extern` functions or `implemented_by`
substitutions. All other dependencies remain forbidden, including `sorryAx`,
arbitrary assumptions and assumptions inside the decision procedure itself.

A generated-looking name is never sufficient evidence. Even a forged name can
only pass this path if the corresponding computational fact is independently
proved by kernel reduction. The record therefore says **kernel-discharged
native facts**, not source-provenance attestation. A failed replay or resource
limit does not establish that the mathematical claim is false.

## Existing results and costs

The correction reviews every completed Lean report under one policy. The
affected regrading scope consists of every final audit rejection, including
the `sorry` controls. Earlier accepted reports already satisfy the stricter
axiom subset. Missing submissions, compile failures, fixed-goal failures and
interrupted or timed-out model attempts are not converted into successes.

Original attempts, claims, submissions, reports and checksums remain unchanged.
Versioned adjudication records retain the old decision, new checker trace,
source hashes, proof/package hashes and a link to the original report. Batch
aggregation selects one effective report per attempt, retaining the original
report pointer separately; it does not append another completed model run.

Original model tokens, native turns and execution costs remain unchanged.
Post-hoc checker time and peak memory are recorded separately; no extra model
work is performed and the original two-hour model-attempt limits are not
retroactively extended. Revised scores must be identified as adjudicated
results and remain reproducible alongside the original strict-audit scores.

The frozen initial prompts are retained byte-for-byte. They list the original
standard-axiom rule; this dated adjudication addendum explains how native facts
are now independently discharged by the host. Future attempts record the
grader revision and scorer-source hashes and use the same corrected rule in
both Goal conditions. Native Rocq and the excluded CompCert probe are unaffected.

## Completed correction snapshot

Adjudication `20261110T042924Z-7f7e71d32df3` reviewed 102 completed Lean reports
and regraded all 14 final audit rejections. All 11 native-computation cases
passed independent kernel replay (3 Goal-off, 8 Goal-on); all 3 `sorry` controls
remained rejected. Original and new adjudication checksums were verified after
checking, and original aggregate model costs are identical before and after.

The effective partial-study counts changed from 121 accepted, 76 rejected and
13 timed out to **132 accepted, 65 rejected and 13 timed out**. The number of
completed model attempts remains 210; 66 runs still await package preparation.
On the 51 contexts completed in both languages, the corrected Goal-on result is
44/51 for Lean and 44/51 for Rocq. Goal-off is 18/51 for Lean and 24/51 for Rocq.
These are dated partial-study results, not final language comparisons.

Host re-adjudication took 222.73 seconds with a maximum measured checker cgroup
peak of 2,282,876,928 bytes. It used no additional model tokens. The regression
suite checked 13 end-to-end toy cases plus malformed audit records and incomplete
verification handling, including native/kernel disagreement and forged facts.
The [machine-readable correction snapshot](../benchmarks/construction/native-audit-correction-20261110.json)
records before/after statistics and grader-source hashes; complete private
adjudication records preserve the original-report links and checking traces.
