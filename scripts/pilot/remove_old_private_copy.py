"""Remove only our old workspace copy after verifying the private WSL copy."""
import hashlib,shutil
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2].resolve();old=(ROOT/'benchmarks/pilot-v1/curator').resolve(strict=True)
assert old==ROOT/'benchmarks/pilot-v1/curator' and old.is_dir()
assert PRIVATE.is_dir() and (PRIVATE.stat().st_mode & 0o077)==0
for p in old.rglob('*'):
    assert not p.is_symlink(),p
    if p.is_file():
        q=PRIVATE/p.relative_to(old)
        assert q.is_file() and hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(q.read_bytes()).digest(),p
# Exact target checked above; the verified private copy is retained.
shutil.rmtree(old)
print('Removed the verified old workspace copy; private WSL copy retained.')
