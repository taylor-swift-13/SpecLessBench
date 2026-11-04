"""Extract direct-call graphs from the actual pinned normalized Clight ASTs."""
import hashlib,json,re
from base64_common import CORE,GROUPS
from accounting import now
def main():
    rows=[]
    for name,gid,_,_ in GROUPS:
        for v in range(3):
            p=CORE/f'compcert/ast/{name.upper()}_V{v}.v';text=p.read_text()
            bodies=dict(re.findall(r'^Definition f_(\w+) := \{\|(.*?)^\|\}\.',text,re.M|re.S))
            assert 'main'in bodies,p
            graph={}
            for f,body in bodies.items():
                calls=re.findall(r'\(Scall\s+(?:None|\(Some [^)]*\))\s+\(Evar _(\w+)',body)
                assert len(calls)==body.count('(Scall'),(p,f,'unhandled call expression')
                assert all(t in bodies for t in calls),(p,f,'missing callee body',calls)
                graph[f]=sorted(set(calls))
            def longest(f,seen):
                assert f not in seen,(p,'recursive call graph')
                options=[[f]+longest(c,seen|{f})for c in graph[f]]
                return max(options,key=len)if options else[f]
            chain=longest('main',set());reachable=set()
            def visit(f):
                if f in reachable:return
                reachable.add(f)
                for child in graph[f]:visit(child)
            visit('main');assert len(chain)>=3
            rows.append({'group_id':gid,'variant':v,'ast':p.relative_to(CORE).as_posix(),
              'ast_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'direct_calls':graph,
              'reachable_functions':sorted(reachable),'longest_call_chain':chain,'maximum_direct_call_edges':len(chain)-1,
              'all_direct_callees_have_bodies':True,'recursive':False})
    report={'schema_version':1,'timestamp_utc':now(),'scope':'syntactic main reachability in normalized Clight ASTs; not runtime stack sampling or proof difficulty',
      'io_helpers_included':True,'functions_and_calls':rows,'final_proofs_attempted':False}
    (CORE/'call-graphs.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{'group':r['group_id'],'variant':r['variant'],'call_edges':r['maximum_direct_call_edges'],'chain':r['longest_call_chain']}for r in rows]))
if __name__=='__main__':main()
