"""Append resolution events without erasing the failed attempts."""
from accounting import AUDIT, append, now

for issue, detail in [
    ('CMD-ba1e72190ca6','Annotated the Rocq comparison flag as bool; the revised definitions and goals type-check.'),
    ('CMD-515770c4dc53','The extracted natural-number mask arithmetic overflowed its stack; replaced the mask by Z and reran the full graph corpus.'),
    ('CMD-eecaefab6f4b','The enclosing test failed because of the preceding Rocq runner overflow; the repaired full run passed.')]:
    append(AUDIT/'issues.jsonl',dict(schema_version=1,id=issue,timestamp_utc=now(),kind='resolution',status='resolved',
        revision='design-v0.8.2',resolution=detail,final_target_proofs_attempted=False))
