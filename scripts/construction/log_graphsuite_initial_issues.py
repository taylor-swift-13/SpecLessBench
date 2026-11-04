"""Retain preliminary compiler diagnostics and honest telemetry limits."""
from accounting import AUDIT,append,now

for issue, detail, fix in [
    ('GRAPHSUITE-LEAN-INITIAL','Lean rejected semicolon-separated structure fields and a multiline structure update.',
     'Use individual structure fields and a single valid update expression.'),
    ('GRAPHSUITE-ROCQ-INITIAL','Rocq could not infer the polymorphic state-update value type and the mutant flag type.',
     'Annotate state words as Z and the flag as bool.')]:
    append(AUDIT/'issues.jsonl',dict(schema_version=1,id=issue,timestamp_utc=now(),
        group_id='shared-graphsuite',revision='design-v0.10',kind='preliminary-compile-diagnostic',
        status='fixed-recheck-pending',description=detail,resolution=fix,
        telemetry='preliminary direct check was not instrumented; exact CPU and peak RSS unavailable',
        final_target_proofs_attempted=False))
