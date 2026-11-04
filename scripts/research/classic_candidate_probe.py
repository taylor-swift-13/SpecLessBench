"""Exploratory Python differential probes; NOT formal benchmark implementations.

No external sources are copied. Domains are intentionally bounded. See the
research note before interpreting these tests as evidence.
"""
import argparse, hashlib, itertools, json, random, resource, sys, time
from pathlib import Path

INF=10**9

def floyd(matrix):
    n=len(matrix)
    d=[[0 if i==j else INF if matrix[i][j] is None else matrix[i][j]
        for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k]!=INF and d[k][j]!=INF:
                    d[i][j]=min(d[i][j],d[i][k]+d[k][j])
    return [[None if x==INF else x for x in row] for row in d]

def repeated_dijkstra(matrix, ignore_zero=False):
    n=len(matrix); result=[]
    for start in range(n):
        d=[INF]*n; d[start]=0; seen=[False]*n
        for _ in range(n):
            options=[i for i in range(n) if not seen[i] and d[i]!=INF]
            if not options: break
            u=min(options,key=lambda i:d[i]);seen[u]=True
            for v,w in enumerate(matrix[u]):
                if w is not None and (not ignore_zero or w!=0):
                    d[v]=min(d[v],d[u]+w)
        result.append([None if x==INF else x for x in d])
    return result

def brute(text,pattern):
    for i in range(len(text)-len(pattern)+1):
        if text[i:i+len(pattern)]==pattern:return i
    return -1

def bad_character(text,pattern,mutant=False):
    m=len(pattern)
    if not m:return 0
    right={c:i for i,c in enumerate(pattern)};i=0
    while i<=len(text)-m:
        j=m-1
        while j>=0 and pattern[j]==text[i+j]:j-=1
        if j<0:return i
        i += m if mutant else max(1,j-right.get(text[i+j],-1))
    return -1

def graph_cases(rng):
    pairs=[(i,j) for i in range(3) for j in range(3) if i!=j]
    for weights in itertools.product((None,0,1,2),repeat=len(pairs)):
        a=[[None]*3 for _ in range(3)]
        for (u,v),w in zip(pairs,weights):a[u][v]=w
        yield a
    for _ in range(10000):
        n=rng.randrange(1,9)
        yield [[None if i==j or rng.randrange(4)==0 else rng.randrange(10)
                for j in range(n)] for i in range(n)]

def string_cases(rng):
    for n in range(7):
        for t in itertools.product(range(2),repeat=n):
            for m in range(5):
                for p in itertools.product(range(2),repeat=m):yield [list(t),list(p)]
    for _ in range(10000):
        yield [[rng.randrange(4) for _ in range(rng.randrange(49))],
               [rng.randrange(4) for _ in range(rng.randrange(17))]]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=('graph','string'));a=parser.parse_args()
    start=time.monotonic();seed=2026110409 if a.kind=='graph' else 2026110410
    rng=random.Random(seed);cases=graph_cases(rng) if a.kind=='graph' else string_cases(rng)
    seen=set();digest=hashlib.sha256();count=0;dupes=0;distinguishing=0;witness=None;coverage={}
    for x in cases:
        encoded=json.dumps(x,separators=(',',':'));key=encoded
        if key in seen:dupes+=1;continue
        seen.add(key);count+=1;digest.update((encoded+'\n').encode())
        if a.kind=='graph':
            ref=floyd(x);positive=repeated_dijkstra(x);negative=repeated_dijkstra(x,True)
            coverage['zero_weight_graphs']=coverage.get('zero_weight_graphs',0)+int(any(v==0 for row in x for v in row if v is not None))
            coverage['unreachable_graphs']=coverage.get('unreachable_graphs',0)+int(any(v is None for row in ref for v in row))
        else:
            ref=brute(*x);positive=bad_character(*x);negative=bad_character(*x,mutant=True)
            coverage['empty_patterns']=coverage.get('empty_patterns',0)+int(not x[1])
            coverage['matches']=coverage.get('matches',0)+int(ref!=-1)
        if ref!=positive:raise AssertionError(json.dumps({'input':x,'left':ref,'right':positive}))
        if ref!=negative:
            distinguishing+=1
            candidate={'input':x,'reference':ref,'mutant':negative}
            if witness is None or len(encoded)<len(json.dumps(witness['input'],separators=(',',':'))):witness=candidate
    assert distinguishing>0
    root=Path(__file__).resolve().parents[2]
    report={'schema_version':1,'scope':'exploratory Python only; not a benchmark task or proof',
      'kind':a.kind,'seed':seed,'unique_inputs':count,'duplicate_inputs_removed':dupes,'input_stream_sha256':digest.hexdigest(),
      'random_attempts':10000,'unexpected_positive_differences':0,'negative_distinguishing_inputs':distinguishing,
      'witness':witness,'coverage':coverage,'wall_seconds':time.monotonic()-start,
      'max_process_rss_bytes_linux':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'final_proofs_attempted':False,'lean_rocq_compcert_implementations':False}
    out=root/'benchmarks/research/classic-probes'/f'{a.kind}.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
