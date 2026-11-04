"""Replay selected C outputs against structurally independent bounded oracles.

The oracles are curator-only differential checks, never solver specifications.
"""
import argparse,gzip,hashlib,json
from collections import deque
from pathlib import Path
from graphsuite_common import ROOT,CORE,BUILD,GROUPS
from differential_graphsuite import read_c

def oracle(family,x):
    if family=='apsp':
        n=x[0];a=x[1:];out=[]
        for start in range(n):
            d=[None]*n;d[start]=0
            for _ in range(n-1):
                previous=d[:]
                for u in range(n):
                    for v in range(n):
                        w=a[u*n+v]
                        if w>=0 and previous[u] is not None:
                            z=previous[u]+w
                            if d[v] is None or z<d[v]:d[v]=z
            out.extend(-1 if z is None else z for z in d)
        return out
    if family=='scc':
        n=x[0];a=x[1:];reach=[]
        for start in range(n):
            seen={start};q=deque([start])
            while q:
                u=q.popleft()
                for v in range(n):
                    if a[u*n+v] and v not in seen:seen.add(v);q.append(v)
            reach.append(seen)
        return [int(j in reach[i] and i in reach[j])for i in range(n)for j in range(n)]
    n,m=x[:2];text=x[2:2+n];pat=x[2+n:]
    return [next((i for i in range(n-m+1)if text[i:i+m]==pat),-1)]

def main():
    p=argparse.ArgumentParser();p.add_argument('family',choices=[g[0]for g in GROUPS]);args=p.parse_args()
    report=json.loads((CORE/'evidence'/f'{args.family}.json').read_text())
    corpus=ROOT/report['corpus']
    with gzip.open(corpus,'rt')as stream:cases=[json.loads(line)for line in stream]
    candidates=[]
    for path in (BUILD/'runs').glob(args.family+'-*/cases.jsonl.gz'):
        if hashlib.sha256(path.read_bytes()).hexdigest()==report['corpus_sha256'] and (path.parent/'c0.out').exists():candidates.append(path.parent/'c0.out')
    assert candidates,'selected C output not present; rerun full differential first'
    output=candidates[-1];values=read_c(output);assert len(values)==len(cases)==report['case_count']
    for i,(x,value)in enumerate(zip(cases,values)):
        expected=oracle(args.family,x)
        assert value==[len(expected),*expected],(i,x,value,expected)
    dest=CORE/'evidence/oracles';dest.mkdir(parents=True,exist_ok=True)
    packed=dest/f'{args.family}-c0.bin.gz'
    with packed.open('wb')as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0)as stream:stream.write(output.read_bytes())
    evidence={'schema_version':1,'family':args.family,'case_count':len(cases),'unexpected_differences':0,
        'oracle':{'apsp':'repeated Bellman–Ford relaxation','scc':'per-vertex breadth-first reachability','search':'direct Python slice scan'}[args.family],
        'scope':'curator-only independent algorithm against the C reference outputs; not a proof or solver specification',
        'corpus_sha256':report['corpus_sha256'],'reference_output_gzip':packed.relative_to(ROOT).as_posix(),
        'reference_output_gzip_sha256':hashlib.sha256(packed.read_bytes()).hexdigest(),
        'oracle_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (dest/f'{args.family}.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence))
if __name__=='__main__':main()
