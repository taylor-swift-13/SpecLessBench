"""History-biased, deduplicated inputs; no separate correct-output oracle."""
import itertools,random
def flat(rows):return [v for row in rows for v in row]
def feed(data=()):return [0,len(data),*data,*([0]*(8-len(data)))]
def control(op):return [op,*([0]*9)]
def trace(rows,cap=None):return ([len(rows)]if cap is None else[cap,len(rows)])+flat(rows)
def frame(tag,payload):
    data=[tag,len(payload),*payload];check=0
    for v in data:check^=v
    return data+[check]
def valid_domain(f,x):
    if not x:return False
    n=x[0]
    if f==0:
        if not(0<=n<=64 and len(x)==1+10*n):return False
        for i in range(n):
            op,k,*data=x[1+10*i:11+10*i]
            if not(0<=op<=2 and 0<=k<=8 and(op==0 or k==0)and all(0<=v<=255 for v in data[:k])and all(v==0 for v in data[k:])):return False
        return True
    if f==1:
        return 0<=n<=64 and len(x)==1+3*n and all(0<=x[1+3*i]<=5 and
          (0<=x[2+3*i]<=7 and(-1000<=x[3+3*i]<=1000 if x[1+3*i]==0 else x[3+3*i]==0)if x[1+3*i]<3 else x[2+3*i]==0 and x[3+3*i]==0)for i in range(n))
    return len(x)>=2 and 0<=n<=8 and 0<=x[1]<=64 and len(x)==2+3*x[1] and all(0<=x[2+3*i]<=4 and 0<=x[3+3*i]<=(8 if x[2+3*i]==4 else 15)and(-1000<=x[4+3*i]<=1000 if x[2+3*i]==0 else x[4+3*i]==0)for i in range(x[1]))
def valid(f,x):return valid_domain(f,x)
def domain_for(f,x):return f
def corpus(f,random_count,smoke):
    result=[];seen=set();counts={k:0 for k in('witness','boundary','exhaustive','partition','random','stress')};duplicates=0
    def add(x,origin='boundary'):
        nonlocal duplicates
        assert valid(f,x),(f,x)
        key=tuple(x)
        if key in seen:duplicates+=1;return
        seen.add(key);result.append(x);counts[origin]+=1
    witnesses=[trace([feed([1]),feed(),control(1)]),trace([(3,0,0),(3,0,0),(0,0,7),(4,0,0),(5,0,0),(2,0,0)]),
      trace([(0,0,1),(0,1,2),(1,0,0),(0,2,3),(1,1,0)],2)]
    add(witnesses[f],'witness');rng=random.Random(2026110305+f)
    if f==0:
        add(trace([]));add(trace([control(1)]));add(trace([control(2)]));add(trace([feed()]*64),'stress')
        for data in ([0],[1],[1,9],[1,255],frame(1,[]),frame(3,list(range(8))),[1,0,0],frame(2,[0])+[1],frame(2,[])+[0],frame(1,[])+frame(2,[])):
            cmds=[feed(data[i:i+8])for i in range(0,len(data),8)]+[control(1),feed([255]),control(2),feed(frame(1,[]))]
            add(trace(cmds))
        for k in range(64):
            data=frame(k%3+1,[k%256]);cmds=[feed(data)]*k+[control(1)]
            if len(cmds)<=64:add(trace(cmds),'stress')
        if not smoke:
            actions=[feed(),feed([1]),feed(frame(1,[])),feed([0]),control(1),control(2),feed([1,0])]
            for n in range(6):
                for ops in itertools.product(actions,repeat=n):add(trace(ops),'exhaustive')
            for tag in range(1,4):
                for n in range(3):
                    for payload in itertools.product((0,1,255),repeat=n):
                        data=frame(tag,list(payload))
                        for bits in itertools.product((0,1),repeat=len(data)-1):
                            cuts=[0]+[i+1 for i,v in enumerate(bits)if v]+[len(data)]
                            chunks=[feed(data[a:b])for a,b in zip(cuts,cuts[1:])]
                            add(trace(chunks+[control(1)]),'partition')
                            add(trace([item for chunk in chunks for item in(chunk,feed())]+[control(1)]),'partition')
        for j in range(random_count):
            q=rng.randrange(65);ops=[];remaining=[]
            for _ in range(q):
                choose=rng.randrange(12)
                if choose==0:ops.append(control(1))
                elif choose==1:ops.append(control(2));remaining=[]
                elif choose==2:ops.append(feed())
                else:
                    if j%4==0:data=[rng.randrange(256)for _ in range(rng.randrange(9))]
                    else:
                        if not remaining:
                            remaining=frame(rng.randint(1,3),[rng.randrange(256)for _ in range(rng.randrange(9))])
                            if j%4==1 and rng.randrange(6)==0:remaining[-1]^=1
                            if j%4==2 and rng.randrange(8)==0:remaining[1]=rng.choice((9,32,255))
                        take=rng.randint(1,min(8,len(remaining)));data=remaining[:take];remaining=remaining[take:]
                    ops.append(feed(data))
            add(trace(ops),'random')
    elif f==1:
        add(trace([]));add(trace([(4,0,0),(5,0,0),(2,0,0)]));add(trace([(0,0,1),(2,0,0),(1,0,0),(2,0,0)]))
        add(trace([(3,0,0)]*9+[(0,7,1000)]+[(5,0,0)]*9),'stress')
        add(trace([(3,0,0)]*8+[(0,7,-1000)]*48+[(4,0,0)]*7+[(5,0,0)]),'stress')
        add(trace([(0,0,-1000),(3,0,0),(1,0,0),(3,0,0),(0,0,1000),(5,0,0),(4,0,0),(2,0,0)]))
        if not smoke:
            actions=[(0,0,1),(0,1,-1),(1,0,0),(2,0,0),(2,1,0),(3,0,0),(4,0,0),(5,0,0)]
            for n in range(6):
                for ops in itertools.product(actions,repeat=n):add(trace(ops),'exhaustive')
        for j in range(random_count):
            q=rng.randrange(65);ops=[]
            for i in range(q):
                op=rng.choice((0,0,1,2,3,3,4,5))
                key=rng.randrange(8)if op<3 else 0
                value=rng.randint(-1000,1000)if op==0 else 0
                ops.append((op,key,value))
            if j%4==0 and q>=6:
                k=rng.randrange(8);ops[:6]=[(3,0,0),(3,0,0),(0,k,rng.randint(-1000,1000)),(4,0,0),(5,0,0),(2,k,0)]
            add(trace(ops),'random')
    else:
        for cap in range(9):
            add(trace([],cap));add(trace([(0,k,k-8)for k in range(16)]+[(1,k,0)for k in range(16)]+[(4,0,0),(4,8,0)]+[(0,k,1000)for k in range(16)],cap),'stress')
        add(trace([(0,0,1),(0,1,2),(2,0,0),(0,2,3),(1,1,0),(3,2,0),(4,0,0)],2))
        add(trace([(0,0,-1000),(0,0,1000),(4,0,0),(0,1,0),(4,8,0),(0,15,1)],1))
        add(trace([(2,0,0),(3,0,0),(0,0,1),(0,1,2),(4,0,0),(2,0,0)],2))
        if not smoke:
            actions=[(0,0,0),(0,1,1),(1,0,0),(1,1,0),(2,0,0),(3,0,0),(4,0,0),(4,2,0)]
            for cap in range(4):
                for n in range(5):
                    for ops in itertools.product(actions,repeat=n):add(trace(ops,cap),'exhaustive')
        for j in range(random_count):
            cap=rng.randrange(9);q=rng.randrange(65);ops=[]
            for _ in range(q):
                op=rng.choice((0,0,0,1,1,2,3,4));key=rng.randrange(9 if op==4 else(4 if j%2 else 16));v=rng.randint(-1000,1000)if op==0 else 0
                ops.append((op,key,v))
            add(trace(ops,cap),'random')
    return result,counts,duplicates
def invalid_cases(f):
    return {0:[[],[-1],[1,0,9]+[0]*8,trace([[1,1,0,0,0,0,0,0,0,0]]),trace([[0,0,1,0,0,0,0,0,0,0]]),trace([feed([256])])],
      1:[[],[-1],[1,6,0,0],[1,0,8,0],[1,2,0,1],[1,3,1,0],[1,0,0,1001]],
      2:[[],[-1,0],[9,0],[1,1,5,0,0],[1,1,4,9,0],[1,1,2,0,1],[1,1,0,16,0],[1,65]+[1,0,0]*65]}[f]

def observation_features(f,x,raw):
    """Audit output shape and count observed events, not compute correct outputs."""
    from collections import Counter
    c=Counter();assert raw and raw[0]==len(raw)-1;p=1
    if f==0:
        prior_pending=0;prior_code=0
        for i in range(x[0]):
            op,code,pos,base,n=raw[p:p+5];p+=5
            assert op==x[1+10*i]and 0<=code<=4 and 0<=base<=512 and 0<=n<=6
            assert (pos==-1 if code==0 else 0<=pos<=512)
            c['stream-status-'+str(code)]+=1
            if n:c['frame-completed']+=n
            if n>1:c['multi-frame-feed']+=1
            if base>=32:c['stream-offset-32']+=1
            if op==0 and x[2+10*i]==0 and prior_pending>0 and prior_code==0:c['empty-feed-with-pending']+=1
            if op==2 and prior_code!=0:c['reset-after-error']+=1
            for _ in range(n):
                tag,k=raw[p:p+2];assert 1<=tag<=3 and 0<=k<=8;p+=2+k
            k=raw[p];p+=1;assert 0<=k<=18 and all(0<=b<=255 for b in raw[p:p+k]);p+=k
            prior_pending=k;prior_code=code
    elif f==1:
        prior_depth=0
        for i in range(x[0]):
            op,code,found,v,depth=raw[p:p+5];p+=5
            assert op==x[1+3*i]and 0<=code<=2 and found in(0,1)and 0<=depth<=8 and -1000<=v<=1000
            if code==1:c['no-active-error']+=1
            if code==2:c['depth-limit-error']+=1
            if op==4 and code==0 and prior_depth>1:c['nested-commit']+=1
            if op==5 and code==0:c['rollback']+=1
            if op in(0,1)and prior_depth>0:c['write-in-transaction']+=1
            if op==2:c['get-found'if found else'get-missing']+=1
            prior_depth=depth
        assert raw[p]==prior_depth;p+=1
        for _ in range(8):
            found,v=raw[p:p+2];p+=2;assert found in(0,1)and -1000<=v<=1000 and(found or v==0)
    else:
        for i in range(x[1]):
            op,status,v,n=raw[p:p+4];p+=4
            assert op==x[2+3*i]and status in(0,1)and 0<=n<=8
            if op in(1,2):c[('get-'if op==1 else'peek-')+('hit'if status else'miss')]+=1
            if op==0 and not status:c['put-zero-cap']+=1
            if n:c['eviction']+=n
            if op==4 and n:c['resize-eviction']+=n
            if op==4 and v==0:c['resize-zero']+=1
            if op==3:c['erased'if status else'erase-miss']+=1
            for _ in range(n):
                k,v=raw[p:p+2];p+=2;assert 0<=k<=15 and -1000<=v<=1000
        cap,n=raw[p:p+2];p+=2;assert 0<=n<=cap<=8;keys=[]
        for _ in range(n):
            k,v=raw[p:p+2];p+=2;assert 0<=k<=15 and -1000<=v<=1000;keys.append(k)
        assert len(keys)==len(set(keys))
    assert p==len(raw)
    return c
REQUIRED_FEATURES=[
 {'stream-status-'+str(i)for i in range(5)}|{'frame-completed','multi-frame-feed','stream-offset-32','empty-feed-with-pending','reset-after-error'},
 {'no-active-error','depth-limit-error','nested-commit','rollback','write-in-transaction','get-found','get-missing'},
 {'get-hit','get-miss','peek-hit','peek-miss','put-zero-cap','eviction','resize-eviction','resize-zero','erased','erase-miss'}]
