"""Audit opaque index and detect explicit legacy-label leakage risks.

Aggregate counts only: the public report never publishes the private mapping.
Finding no string is not evidence that a release is contamination-free.
"""
import hashlib,json,re,sys
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1'
sys.path.insert(0,str(ROOT/'scripts/pilot'))
from verify_freeze import main as verify
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    verify();manifest=json.loads((P/'manifest.json').read_text());private=json.loads((PRIVATE/'mapping.json').read_text())
    public=json.dumps(manifest,ensure_ascii=False).lower()
    leaked=[row for row in private['contexts'] if row['source_context_id'].lower() in public]
    assert not leaked,'Public pilot manifest embeds a curator task identifier'
    explicit_id=re.compile(r'(?:CEX|COUNTEREXAMPLE|MUTANT|UNSTABLE)',re.I)
    legacy_ids=sum(bool(explicit_id.search(r['source_context_id']))for r in private['contexts'])
    source_hints=re.compile(r'\b(?:mutant|buggy|incorrect|wrong)\b',re.I)
    relevant=[r for r in private['protected_files'] if r['path'].endswith(('.lean','.v','.c','.h'))]
    hint_files=[r for r in relevant if source_hints.search((ROOT/r['path']).read_text(encoding='utf-8',errors='replace'))]
    report={'schema_version':1,'public_manifest_sha256':sha(P/'manifest.json'),
      'public_ids_checked':len(private['contexts']),'curator_ids_in_public_manifest':len(leaked),
      'legacy_context_ids_with_explicit_polarity_words':legacy_ids,
      'protected_source_files_with_explicit_hint_words':len(hint_files),
      'solver_package_verified':False,'isolated_grader_verified':False,
      'release_ready':False,'reason':'Opaque index is not a solver package. Shared source files, legacy goal symbols, evidence and public Git history require separate leakage and isolation review.',
      'limitations':['Regex checks explicit words only; variant patterns and public history can also leak labels.',
                     'No genuine solver-facing package has yet passed a per-task disclosure audit.']}
    (P/'leak-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
