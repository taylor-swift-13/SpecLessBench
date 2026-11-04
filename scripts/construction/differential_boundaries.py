"""Nine executions/input: sanitized C, Lean, extracted Rocq; no Clight runs."""
import argparse,gzip,hashlib,json,os,struct
from pathlib import Path
from boundaries_common import CORE,BUILD,GROUPS,LEAN
from boundary_cases import corpus,invalid_cases,valid,valid_domain,domain_for
from accounting import ROOT,AUDIT,append,now
from measure import measured

def read_c(path):
    out=[]
    with path.open('rb')as stream:
        while head:=stream.read(4):
            n=struct.unpack('<i',head)[0];assert 0<=n<8192
            data=stream.read(4*n);assert len(data)==4*n
            out.append([n,*struct.unpack('<'+str(n)+'i',data)])
    return out
def native(path):
    return [None if line.strip()=='FAIL'else list(map(int,line.split()))for line in path.read_text().splitlines()]

def main():
    p=argparse.ArgumentParser();p.add_argument('--family',choices=[g[0]for g in GROUPS],required=True)
    p.add_argument('--random-cases',type=int,default=5000);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    f=next(i for i,g in enumerate(GROUPS)if g[0]==a.family);name,gid,contexts,_=GROUPS[f]
    xs,counts,duplicates=corpus(f,a.random_cases,a.smoke);bad=invalid_cases(f);assert all(not valid(f,x)for x in bad)
    folder=BUILD/'runs'/(name+'-'+now().replace(':','').replace('.',''));folder.mkdir(parents=True)
    compressed=folder/'cases.jsonl.gz'
    with compressed.open('wb')as raw:
        with gzip.GzipFile(fileobj=raw,mode='wb',filename='',mtime=0)as gz:
            for x in xs:gz.write((json.dumps(x,separators=(',',':'))+'\n').encode())
    binfile=folder/'input.bin';txt=folder/'input.txt'
    with binfile.open('wb')as b,txt.open('w')as t:
        for x in xs:
            b.write(struct.pack('<'+str(len(x)+1)+'i',len(x),*x));suffix=' '.join(map(str,x))
            for style in (99,0,1,2):t.write(f'{f} {style} {suffix}\n')
        for x in bad:t.write(f'{f} 99 '+' '.join(map(str,x))+'\n')
    harness=folder/'harness.c'
    harness.write_text('#define main eb_entry\n#include EB_PROGRAM\n#undef main\n#include <stdio.h>\n'
      'int main(void){int i,n,k;while(fread(&k,sizeof(int),1,stdin)==1){if(k<0||k>8192)return 7;'
      'for(i=0;i<8192;i++)eb_input[i]=0;if(fread(eb_input,sizeof(int),k,stdin)!=(unsigned)k)return 8;'
      'if(eb_entry()!=0)return 2;n=eb_output[0];if(n<0||n>=8192)return 3;'
      'for(i=n+1;i<8192;i++)if(eb_output[i]!=0)return 4;'
      'if(fwrite(eb_output,sizeof(int),n+1,stdout)!=(unsigned)(n+1))return 5;}return ferror(stdin)?6:0;}\n')
    cs=[]
    for style in range(3):
        pre=folder/f'v{style}.c';exe=folder/f'v{style}';out=folder/f'c{style}.out'
        measured(['gcc','-E','-P','-std=c99',str(CORE/'c'/name/f'v{style}.c')],gid,'preprocess',stdout_path=pre)
        measured(['gcc','-std=c99','-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',
          '-DEB_PROGRAM="'+str(pre)+'"',str(harness),'-o',str(exe)],gid,'compile-c-sanitized')
        measured([str(exe)],gid,'execute-c',stdin_path=binfile,stdout_path=out,timeout=900)
        cs.append(read_c(out));assert len(cs[-1])==len(xs)
    os.environ['LEAN_PATH']=str(BUILD/'lean');runs={}
    for platform,cmd in (('lean',[LEAN,'--run',str(CORE/'lean/BoundaryRunner.lean')]),('rocq',[str(BUILD/'rocq/runner')])):
        out=folder/(platform+'.out');measured(cmd,gid,'execute-'+platform,stdin_path=txt,stdout_path=out,timeout=1200)
        runs[platform]=native(out);assert len(runs[platform])==4*len(xs)+len(bad)
    errors=[];negatives=[]
    def error(kind,i,x,outs):errors.append({'kind':kind,'case_index':i,'input':x,'outputs':outs})
    for i,x in enumerate(xs):
        for platform in runs:
            if runs[platform][4*i]!=[1]:error('input-domain-disagreement',i,x,{platform:runs[platform][4*i],'python':True})
        if cs[0][i]!=cs[1][i]:error('unexpected-positive-difference',i,x,{'c0':cs[0][i],'c1':cs[1][i]})
        for style in range(3):
            outs={platform:runs[platform][4*i+1+style]for platform in runs}
            if any(v!=cs[style][i]for v in outs.values()):error('cross-platform-difference-v'+str(style),i,x,{'c':cs[style][i],**outs})
        if cs[0][i]!=cs[2][i]and valid_domain(contexts[1][2],x):negatives.append(i)
    for i,x in enumerate(bad):
        for platform in runs:
            if runs[platform][4*len(xs)+i]!=[0]:error('invalid-domain-disagreement',i,x,{platform:runs[platform][4*len(xs)+i],'python':False})
    for kind in sorted({e['kind']for e in errors}):
        selected=[e for e in errors if e['kind']==kind]
        append(AUDIT/'issues.jsonl',{'schema_version':1,'timestamp_utc':now(),'id':folder.name+'-'+kind,'group_id':gid,'revision':'design-v0.4','kind':kind,'status':'open','occurrences':len(selected),'representative':min(selected,key=lambda e:len(e['input'])),'all_disagreements':str(folder/'disagreements.jsonl.gz')})
    if errors:
        with gzip.open(folder/'disagreements.jsonl.gz','wt')as gz:
            for e in errors:gz.write(json.dumps(e)+'\n')
    witness=None
    if negatives:
        i=min(negatives,key=lambda i:(len(xs[i]),len(str(xs[i]))));witness={'input':xs[i],'v0':cs[0][i],'v2':cs[2][i]}
        append(AUDIT/'issues.jsonl',{'schema_version':1,'timestamp_utc':now(),'id':folder.name+'-retained-negative','group_id':gid,'revision':'design-v0.4','kind':'intentional-negative-observed','status':'retained-as-task','witness':witness,'minimality':'shortest tested input; no global minimality claim','certificate':None})
    hist={}
    if f>=3:
        for out in cs[0]:hist[str(out[1])]=hist.get(str(out[1]),0)+1
        required={3:set(range(5)),4:set(range(8)),5:set(range(4)),6:set(range(3)),7:set(range(2))}[f]
        missing=required-set(map(int,hist))
        if missing:error('reference-error-coverage-missing',-1,[],{'missing':sorted(missing)})
    report={'schema_version':1,'revision':'design-v0.4','group_id':gid,'family':name,'case_count':len(xs),
      'program_executions':9*len(xs),'validity_evaluations':2*(len(xs)+len(bad)),'cases_by_origin':counts,
      'duplicate_inputs_removed':duplicates,'rng_seed':2026110304+f,'random_cases_requested':a.random_cases,
      'exhaustive_scope':'explicit small transport/content subdomains in boundary_cases.py; not entire domain',
      'unexpected_disagreements':len(errors),'negative_distinguishing_inputs':len(negatives),'witness':witness,
      'context_test_counts':{tid:sum(valid_domain(d,x)for x in xs)for tid,_,d in contexts},'reference_status_histogram':hist,
      'corpus':compressed.relative_to(ROOT).as_posix(),'corpus_sha256':hashlib.sha256(compressed.read_bytes()).hexdigest(),
      'registry_sha256':hashlib.sha256((CORE/'groups.json').read_bytes()).hexdigest(),
      'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'corpus_generator_sha256':hashlib.sha256((ROOT/'scripts/construction/boundary_cases.py').read_bytes()).hexdigest(),
      'clight_execution_tested':False,'final_proof_attempted':False,'smoke':a.smoke,
      'status':'failed'if errors or not negatives else 'differential-passed; labels provisional'}
    (CORE/'evidence').mkdir(exist_ok=True);(CORE/'evidence'/(name+('-smoke'if a.smoke else '')+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)
    if errors or not negatives:raise SystemExit('Construction differences retained; repair or revise before freezing')
if __name__=='__main__':main()
