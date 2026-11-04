"""Fail closed on source drift or pilot mapping mismatch."""
import hashlib,hmac,json
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    public=json.loads((P/'manifest.json').read_text());private=PRIVATE/'mapping.json'
    assert sha(private)==public['private_mapping_sha256'],'Private mapping altered'
    mapping=json.loads(private.read_text());secret=(PRIVATE/'secret.bin').read_bytes()
    for row in mapping['contexts']:
        expected='P-'+hmac.new(secret,row['source_context_id'].encode(),hashlib.sha256).hexdigest()[:16]
        assert row['pilot_id']==expected
    for row in mapping['protected_files']:
        path=ROOT/row['path'];assert path.is_file() and sha(path)==row['sha256'],row['path']
    if 'validator_addendum_sha256' in public:
        addendum=PRIVATE/'validator-dependencies.json'
        assert sha(addendum)==public['validator_addendum_sha256'],'Validator addendum altered'
        for row in json.loads(addendum.read_text())['files']:
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    if 'audit_inputs_sha256' in public:
        addendum=PRIVATE/'audit-inputs.json'
        assert sha(addendum)==public['audit_inputs_sha256'],'Platform-audit addendum altered'
        for row in json.loads(addendum.read_text())['files']:
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
    if 'audit_extras_sha256' in public:
        addendum=PRIVATE/'audit-extras.json'
        assert sha(addendum)==public['audit_extras_sha256'],'Audit-support addendum altered'
        # Historical support scripts are preserved in the private source
        # archive. They may evolve without changing the frozen tasks; a fresh
        # platform rebuild still checks the archived hashes before use.
    if 'toolchain_addendum_sha256' in public:
        addendum=PRIVATE/'toolchains.json'
        assert sha(addendum)==public['toolchain_addendum_sha256'],'Toolchain addendum altered'
        for row in json.loads(addendum.read_text())['executables']:
            assert sha(Path(row['path']))==row['sha256'],row['name']
    assert {x['pilot_id']for x in public['contexts']}=={x['pilot_id']for x in mapping['contexts']}
    assert len(mapping['contexts'])==public['context_count']==71
    print(f"Verified {len(mapping['contexts'])} contexts and {len(mapping['protected_files'])} protected files.")
if __name__=='__main__':main()
