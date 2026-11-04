"""Append resolutions after compiler and complete differential checks pass."""
from accounting import AUDIT,append,now
for issue in ('GRAPHSUITE-LEAN-INITIAL','GRAPHSUITE-ROCQ-INITIAL'):
    append(AUDIT/'issues.jsonl',dict(schema_version=1,id=issue,timestamp_utc=now(),
        kind='resolution',status='resolved',revision='design-v0.10',
        resolution='Revised implementation passed the platform build, branch type checks and selected full differential corpus.',
        final_target_proofs_attempted=False))
