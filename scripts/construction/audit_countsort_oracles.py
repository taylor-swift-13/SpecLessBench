"""Check every selected C reference observation using stable Python sorting."""
import gzip,hashlib,json
from pathlib import Path
from countsort_common import ROOT,CORE,BUILD
from differential_countsort import read_c
family='records';report=json.loads((CORE/'evidence/records.json').read_text())
with gzip.open(ROOT/report['corpus'],'rt')as stream:cases=[json.loads(s)for s in stream]
candidates=[]
for p in (BUILD/'runs').glob('records-*/cases.jsonl.gz'):
    if hashlib.sha256(p.read_bytes()).hexdigest()==report['corpus_sha256'] and (p.parent/'c0.out').exists():candidates.append(p.parent/'c0.out')
assert candidates
output=candidates[-1];values=read_c(output);assert len(values)==len(cases)==report['case_count']
for i,(x,raw)in enumerate(zip(cases,values)):
    result=sorted(zip(x[1::2],x[2::2]),key=lambda pair:pair[0]);expected=[v for pair in result for v in pair]
    assert raw==[len(expected),*expected],(i,x,raw,expected)
dest=CORE/'evidence/oracles';dest.mkdir(parents=True,exist_ok=True);packed=dest/'records-c0.bin.gz'
with packed.open('wb')as raw:
    with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0)as gz:gz.write(output.read_bytes())
evidence={'schema_version':1,'family':family,'case_count':len(cases),'unexpected_differences':0,
  'oracle':'Python stable key sort','scope':'curator-side only; not a solver specification or proof',
  'corpus_sha256':report['corpus_sha256'],'reference_output_gzip':packed.relative_to(ROOT).as_posix(),
  'reference_output_gzip_sha256':hashlib.sha256(packed.read_bytes()).hexdigest(),
  'oracle_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(dest/'records.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps(evidence))
