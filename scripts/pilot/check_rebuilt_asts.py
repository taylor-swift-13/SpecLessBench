"""Compare freshly exported ASTs to frozen task ASTs byte for byte."""
import hashlib,json
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1';W=ROOT/'_build/pilot-v1/platform-audit/workspace'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
private=json.loads((PRIVATE/'mapping.json').read_text())
asts=[r for r in private['protected_files'] if '/compcert/ast/' in r['path'] and r['path'].endswith('.v')]
assert len(asts)==103,len(asts)
bad=[r['path'] for r in asts if not (W/r['path']).is_file() or sha(W/r['path'])!=r['sha256']]
report={'schema_version':1,'ast_count':len(asts),'byte_identical_count':len(asts)-len(bad),
        'mismatch_count':len(bad),'scope':'fresh exports compared to frozen original AST source hashes',
        'mismatches_recorded_privately':True}
(P/'ast-audit.json').write_text(json.dumps(report,indent=2)+'\n')
(PRIVATE/'ast-mismatches.json').write_text(json.dumps(bad,indent=2)+'\n')
print(json.dumps(report));assert not bad,'AST regeneration differs from frozen snapshot; inspect private mismatch list.'
