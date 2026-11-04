"""Archive selected full-run corpus, preserving its evidence hash."""
import hashlib,json,shutil
from countsort_common import ROOT,CORE
report_path=CORE/'evidence/records.json';report=json.loads(report_path.read_text());source=ROOT/report['corpus']
dest=CORE/'evidence/corpora/records.jsonl.gz';dest.parent.mkdir(parents=True,exist_ok=True)
if source.resolve()!=dest.resolve():shutil.copyfile(source,dest)
assert hashlib.sha256(dest.read_bytes()).hexdigest()==report['corpus_sha256']
report['corpus']=dest.relative_to(ROOT).as_posix();report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Archived stable counting sort corpus.')
