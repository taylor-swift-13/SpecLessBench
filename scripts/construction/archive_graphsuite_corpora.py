"""Copy successful reproducible corpora out of ignored build directories."""
import hashlib,json,shutil
from graphsuite_common import ROOT,CORE,GROUPS
dest=CORE/'evidence/corpora';dest.mkdir(parents=True,exist_ok=True)
for family,*_ in GROUPS:
    report_path=CORE/'evidence'/f'{family}.json';report=json.loads(report_path.read_text())
    source=ROOT/report['corpus'];target=dest/f'{family}.jsonl.gz'
    if source.resolve()!=target.resolve():shutil.copyfile(source,target)
    assert hashlib.sha256(target.read_bytes()).hexdigest()==report['corpus_sha256']
    report['corpus']=target.relative_to(ROOT).as_posix()
    report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Archived',len(GROUPS),'selected full-test corpora; hashes preserved.')
