"""Three-platform construction tests with deduplication and input-domain audits.

Exhaustive cases are explicitly small, except factorial's full admitted domain.
No equivalence claim or final proof is inferred from successful executable runs.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import os
import random
import struct
import sys
from pathlib import Path
from algorithms_common import CORE, BUILD, GROUPS, LEAN
from accounting import ROOT, AUDIT, append, now
from measure import measured


def valid(f, x):
    if not x: return False
    n=x[0]
    if f==0: return len(x)==1 and 0<=n<=12
    if f in (1,2): return 0<=n<=64 and len(x)==n+1 and all(-1000000<=v<=1000000 for v in x[1:])
    if f==3:
        return len(x)>=3 and all(0<=v<=6 for v in x[:3]) and len(x)==3+x[0]*x[1]+x[1]*x[2] and all(-1000<=v<=1000 for v in x[3:])
    if f==4:
        return len(x)>=2 and 0<=n<=64 and 0<=x[1]<=32 and len(x)==2+n+x[1] and all(0<=v<=255 for v in x[2:])
    return 0<=n<=64 and len(x)==1+2*n and all(0<=x[1+2*i]<=2 and
        (-1000000<=x[2+2*i]<=1000000 if x[1+2*i]==0 else x[2+2*i]==0) for i in range(n))


def corpus(f, random_count, smoke):
    seeds=[[1],[0],[1,1],[1,2,2,1,2,1,2,3,4],[4,3,0,0,0,1,0,0,1],[3,0,1,1,0,1,0]]
    result=[]; seen=set(); counts={"witness":0,"boundary":0,"exhaustive":0,"random":0}; duplicates=0
    def add(x, origin):
        nonlocal duplicates
        assert valid(f,x),(f,x)
        key=tuple(x)
        if key in seen: duplicates+=1; return
        seen.add(key); result.append(x); counts[origin]+=1
    add(seeds[f],"witness")
    rng=random.Random(20261103+f)
    if f==0:
        for n in range(13): add([n],"exhaustive")
        return result,counts,duplicates
    if f in (1,2):
        for data in ([],[1000000],[-1000000],[0]*64,list(range(64)),[1000000]*64,[-1000000]*64): add([len(data),*data],"boundary")
        if not smoke:
            for n in range(8):
                for xs in itertools.product((-1,0,1),repeat=n): add([n,*xs],"exhaustive")
        for _ in range(random_count):
            n=rng.randrange(65); add([n,*[rng.randint(-1000000,1000000) for _ in range(n)]],"random")
    elif f==3:
        for r,k,c in ((0,0,0),(6,6,6),(6,0,6),(0,6,6),(6,6,0)):
            add([r,k,c,*([1000]*(r*k)),*([-1000]*(k*c))],"boundary")
        if not smoke:
            for r,k,c in itertools.product(range(3),repeat=3):
                for xs in itertools.product((-1,0,1),repeat=r*k+k*c): add([r,k,c,*xs],"exhaustive")
        for _ in range(random_count):
            r,k,c=[rng.randrange(7) for _ in range(3)]
            add([r,k,c,*[rng.randint(-1000,1000) for _ in range(r*k+k*c)]],"random")
    elif f==4:
        for text,pat in (([],[]),([],[0]),([0],[]),([0]*63+[1],[0]*31+[1]),([255]*64,[255]*32)):
            add([len(text),len(pat),*text,*pat],"boundary")
        if not smoke:
            for n in range(8):
                for m in range(5):
                    for xs in itertools.product((0,1),repeat=n+m): add([n,m,*xs],"exhaustive")
        for j in range(random_count):
            n=rng.randrange(65); m=rng.randrange(33); alphabet=(2,4,256)[j%3]
            text=[rng.randrange(alphabet) for _ in range(n)]; pat=[rng.randrange(alphabet) for _ in range(m)]
            if j%2==0 and m<=n:
                start=rng.randrange(n-m+1); text[start:start+m]=pat
            add([n,m,*text,*pat],"random")
    else:
        add([0],"boundary")
        add([64,*sum(([0,1000000] for _ in range(64)),[])],"boundary")
        add([64,*sum(([1,0] for _ in range(64)),[])],"boundary")
        if not smoke:
            commands=[[0,-1],[0,0],[0,1],[1,0],[2,0]]
            for n in range(7):
                for trace in itertools.product(commands,repeat=n): add([n,*[v for cmd in trace for v in cmd]],"exhaustive")
        for _ in range(random_count):
            n=rng.randrange(65); cmds=[]
            for _ in range(n):
                op=rng.randrange(3); cmds.extend([op,rng.randint(-1000000,1000000) if op==0 else 0])
            add([n,*cmds],"random")
    return result,counts,duplicates


def invalid_cases(f):
    return {0:[[],[-1],[13],[0,0]],1:[[],[-1],[2,0],[1,1000001],[65]+[0]*65],
        2:[[],[-1],[1],[1,-1000001],[65]+[0]*65],
        3:[[],[7,0,0],[-1,0,0],[1,1,1,1],[1,1,1,1001,0]],
        4:[[],[65,0]+[0]*65,[0,33]+[0]*33,[1,0,256],[1,1,0]],
        5:[[],[-1],[1,3,0],[1,1,1],[65]+[1,0]*65]}[f]


def read_c(path):
    out=[]
    with path.open("rb") as stream:
        while head:=stream.read(4):
            n=struct.unpack("<i",head)[0]; assert 0<=n<8192
            data=stream.read(4*n); assert len(data)==4*n
            out.append([n,*struct.unpack("<"+str(n)+"i",data)])
    return out


def native(path):
    return [None if line.strip()=="FAIL" else list(map(int,line.split())) for line in path.read_text().splitlines()]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family",choices=[g[0] for g in GROUPS],required=True)
    parser.add_argument("--random-cases",type=int,default=5000)
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args(); f=next(i for i,g in enumerate(GROUPS) if g[0]==args.family)
    name,gid,_,_,_=GROUPS[f]; xs,counts,duplicates=corpus(f,args.random_cases,args.smoke)
    bad=invalid_cases(f); assert all(not valid(f,x) for x in bad)
    folder=BUILD/"runs"/(name+"-"+now().replace(":","").replace(".","")); folder.mkdir(parents=True)
    compressed=folder/"cases.jsonl.gz"
    with compressed.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw,mode="wb",filename="",mtime=0) as gz:
            for x in xs: gz.write((json.dumps(x,separators=(",",":"))+"\n").encode())
    binfile=folder/"input.bin"; txt=folder/"input.txt"
    with binfile.open("wb") as b,txt.open("w") as t:
        for x in xs:
            b.write(struct.pack("<"+str(len(x)+1)+"i",len(x),*x))
            suffix=" ".join(map(str,x))
            for style in (99,0,1,2): t.write(f"{f} {style} {suffix}\n")
        for x in bad: t.write(f"{f} 99 "+" ".join(map(str,x))+"\n")
    harness=folder/"harness.c"
    harness.write_text('#define main eb_entry\n#include EB_PROGRAM\n#undef main\n#include <stdio.h>\n'
        'int main(void){int i,n,k;while(fread(&k,sizeof(int),1,stdin)==1){if(k<0||k>8192)return 7;'
        'for(i=0;i<8192;i++)eb_input[i]=0;if(fread(eb_input,sizeof(int),k,stdin)!=(unsigned)k)return 8;'
        'if(eb_entry()!=0)return 2;n=eb_output[0];if(n<0||n>=8192)return 3;'
        'for(i=n+1;i<8192;i++)if(eb_output[i]!=0)return 4;'
        'if(fwrite(eb_output,sizeof(int),n+1,stdout)!=(unsigned)(n+1))return 5;}return ferror(stdin)?6:0;}\n')
    cs=[]
    for style in range(3):
        pre=folder/f"v{style}.c"; exe=folder/f"v{style}"; out=folder/f"c{style}.out"
        measured(["gcc","-E","-P","-std=c99",str(CORE/"c"/name/f"v{style}.c")],gid,"preprocess",stdout_path=pre)
        measured(["gcc","-std=c99","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-no-pie",
            '-DEB_PROGRAM="'+str(pre)+'"',str(harness),"-o",str(exe)],gid,"compile-c-sanitized")
        measured([str(exe)],gid,"execute-c",stdin_path=binfile,stdout_path=out,timeout=900)
        cs.append(read_c(out)); assert len(cs[-1])==len(xs)
    os.environ["LEAN_PATH"]=str(BUILD/"lean")
    runs={}
    for p,cmd in (("lean",[LEAN,"--run",str(CORE/"lean/BasicRunner.lean")]),("rocq",[str(BUILD/"rocq/runner")])):
        out=folder/(p+".out"); measured(cmd,gid,"execute-"+p,stdin_path=txt,stdout_path=out,timeout=1200)
        runs[p]=native(out); assert len(runs[p])==4*len(xs)+len(bad)
    errors=[]; negatives=[]
    def record(kind,index,input_value,outputs):
        item={"kind":kind,"case_index":index,"input":input_value,"outputs":outputs}
        errors.append(item)
    for i,x in enumerate(xs):
        for p in runs:
            if runs[p][4*i]!=[1]: record("input-domain-disagreement",i,x,{p:runs[p][4*i],"python":True})
        if cs[0][i]!=cs[1][i]: record("unexpected-positive-difference",i,x,{"c0":cs[0][i],"c1":cs[1][i]})
        for style in range(3):
            outputs={p:runs[p][4*i+1+style] for p in runs}
            if any(v!=cs[style][i] for v in outputs.values()): record("cross-platform-difference-v"+str(style),i,x,{"c":cs[style][i],**outputs})
        if cs[0][i]!=cs[2][i]: negatives.append(i)
    for i,x in enumerate(bad):
        for p in runs:
            if runs[p][4*len(xs)+i]!=[0]: record("invalid-domain-disagreement",i,x,{p:runs[p][4*len(xs)+i],"python":False})
    for kind in sorted({e["kind"] for e in errors}):
        selected=[e for e in errors if e["kind"]==kind]
        append(AUDIT/"issues.jsonl",{"schema_version":1,"timestamp_utc":now(),"id":folder.name+"-"+kind,
            "group_id":gid,"revision":"design-v0.3.1","kind":kind,"status":"open","occurrences":len(selected),
            "representative":min(selected,key=lambda e:len(e["input"])),"all_disagreements":str(folder/"disagreements.jsonl.gz")})
    if errors:
        with gzip.open(folder/"disagreements.jsonl.gz","wt") as gz:
            for e in errors: gz.write(json.dumps(e)+"\n")
    witness=None
    if negatives:
        i=min(negatives,key=lambda i:(len(xs[i]),len(str(xs[i])))); witness={"input":xs[i],"v0":cs[0][i],"v2":cs[2][i]}
        append(AUDIT/"issues.jsonl",{"schema_version":1,"timestamp_utc":now(),"id":folder.name+"-retained-negative",
            "group_id":gid,"revision":"design-v0.3.1","kind":"intentional-negative-observed","status":"retained-as-task",
            "witness":witness,"minimality":"shortest tested input; no global minimality claim","certificate":None})
    registry=CORE/"groups.json"
    report={"schema_version":1,"revision":"design-v0.3.1","group_id":gid,"family":name,"case_count":len(xs),
        "program_executions":9*len(xs),"validity_evaluations":2*(len(xs)+len(bad)),"cases_by_origin":counts,
        "duplicate_inputs_removed":duplicates,"rng_seed":20261103+f,"random_cases_requested":args.random_cases,
        "exhaustive_scope":"entire admitted factorial value domain" if f==0 else "explicit small domain; see corpus generator",
        "unexpected_disagreements":len(errors),"negative_distinguishing_inputs":len(negatives),"witness":witness,
        "corpus":compressed.relative_to(ROOT).as_posix(),"corpus_sha256":hashlib.sha256(compressed.read_bytes()).hexdigest(),
        "registry_sha256":hashlib.sha256(registry.read_bytes()).hexdigest(),"generator_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "clight_execution_tested":False,"final_proof_attempted":False,"smoke":args.smoke,
        "status":"failed" if errors or not negatives else "differential-passed; labels provisional"}
    (CORE/"evidence").mkdir(exist_ok=True)
    (CORE/"evidence"/(name+("-smoke" if args.smoke else "")+".json")).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report),flush=True)
    if errors or not negatives: raise SystemExit("Construction differences retained; repair or revise before freezing")


if __name__=="__main__": main()
