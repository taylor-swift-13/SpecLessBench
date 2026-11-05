"""Freeze executable fingerprints; libraries and OS are not fully locked."""
import hashlib,json,platform
from pathlib import Path
from private_paths import PRIVATE
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot';out=PRIVATE/'toolchains.json'
if out.exists():raise SystemExit('Toolchain addendum exists.')
tools={'lean':'/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean',
       'rocq':'/home/yangfp/.opam/qcp-8.20/bin/coqc','compcert_rocq':'/home/yangfp/.opam/five/bin/coqc',
       'clightgen':'/home/yangfp/.opam/five/bin/clightgen','bubblewrap':'/usr/bin/bwrap'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
record={'executables':[{'name':k,'path':v,'sha256':sha(v)}for k,v in tools.items()],
        'system':platform.platform(),'full_library_and_os_lock':False,
        'limitation':'Executable fingerprints do not pin the complete standard libraries, installed packages or kernel.'}
out.write_text(json.dumps(record,indent=2)+'\n');m=json.loads((P/'manifest.json').read_text())
m['toolchain_addendum_sha256']=sha(out);m['complete_environment_lock']=False
(P/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
print('Bound tool executables; full environment lock remains pending.')
