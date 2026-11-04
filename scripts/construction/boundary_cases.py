"""Transport domains and reproducible corpora; malformed *content* is admitted."""
import itertools,random

def valid_domain(d,x):
    if not x:return False
    n=x[0]
    if d==0:
        if not(0<=n<=64 and len(x)==1+3*n):return False
        children=[]
        for i in range(n):
            v,l,r=x[1+3*i:4+3*i]
            if not(-1000<=v<=1000 and all(c==-1 or 0<=c<i for c in (l,r))):return False
            children += [c for c in (l,r) if c>=0]
        return len(set(children))==len(children)
    if d in (1,2,3,4,7) and len(x)<2:return False
    if d==1:
        q=x[1]
        return 1<=n<=64 and 0<=q<=64 and len(x)==2+3*q and all(0<=x[2+3*i]<=1 and 0<=x[3+3*i]<n and 0<=x[4+3*i]<n for i in range(q))
    if d==2:
        q=x[1]
        return n==0 and 0<=q<=64 and len(x)==2+2*q and all(0<=x[2+2*i]<=3 and (-1000000<=x[3+2*i]<=1000000 if x[2+2*i]==0 else x[3+2*i]==0) for i in range(q))
    if d==3:return n==1 and 0<=x[1]<=64 and len(x)==2+x[1] and all(-1000000<=v<=1000000 for v in x[2:])
    if d==4:
        e=x[1]
        if not(1<=n<=64 and 0<=e<=8 and len(x)==2+e+3*n and all(-1000<=v<=1000 for v in x[2:2+e])):return False
        for i in range(n):
            tag,a,b=x[2+e+3*i:5+e+3*i]
            if not 0<=tag<=255:return False
            if tag==0:ok=-1000<=a<=1000 and b==0
            elif tag==1:ok=0<=a<=15 and b==0
            elif tag>10:ok=-1000<=a<=1000 and -1000<=b<=1000
            else:ok=0<=a<i and (b==0 if tag in (8,9) else 0<=b<i)
            if not ok:return False
        return True
    if d==7:return 0<=n<=64 and 0<=x[1]<=96 and len(x)==2+n and all(0<=v<=255 for v in x[2:])
    return 0<=n<=(96 if d==5 else 64) and len(x)==1+n and all(0<=v<=255 for v in x[1:])

def domain_for(f,x):return f if f<2 else (2 if x and x[0]==0 else 3) if f==2 else f+1
def valid(f,x):return valid_domain(domain_for(f,x),x)
def flat(records):return [v for row in records for v in row]
def ast(nodes,env=()):return [len(nodes),len(env),*env,*flat(nodes)]
def stream(data,cap=None):return [len(data),*([cap] if cap is not None else []),*data]
def record(tag,payload):
    data=[tag,len(payload),0,*payload];checksum=0
    for b in data:checksum^=b
    return data+[checksum]

def corpus(f,random_count,smoke):
    result=[];seen=set();counts={k:0 for k in ('witness','boundary','exhaustive','random')};duplicates=0
    def add(x,origin='boundary'):
        nonlocal duplicates
        assert valid(f,x),(f,x)
        key=tuple(x)
        if key in seen:duplicates+=1;return
        seen.add(key);result.append(x);counts[origin]+=1
    witnesses=[
        [3,0,-1,-1,1,0,-1,2,1,-1],
        [4,4,0,0,1,0,2,3,0,1,3,1,0,3],
        [1,4,9,7,8,1],
        ast([(0,0,0),(1,0,0),(6,0,1)]),
        stream(record(1,[1,2])),stream([34,34]),stream([255,65],4),stream(list(b'../..'))]
    add(witnesses[f],'witness');rng=random.Random(2026110304+f)
    if f==0:
        add([0])
        for n in (1,2,3,64):
            for side in (0,1):add([n,*flat([(i, i-1 if i and side==0 else -1,i-1 if i and side==1 else -1) for i in range(n)])])
        if not smoke:
            for n in range(4):
                choices=[list(itertools.product(range(-1,i),repeat=2)) for i in range(n)]
                for edges in itertools.product(*choices):
                    x=[n,*flat([(i%2,*e)for i,e in enumerate(edges)])]
                    if valid(f,x):add(x,'exhaustive')
        for _ in range(random_count):
            n=rng.randrange(65);free=[];nodes=[]
            for i in range(n):
                ch=[]
                for _ in range(2):
                    c=rng.choice([-1,*free]);ch.append(c)
                    if c>=0:free.remove(c)
                nodes.append((rng.randint(-1000,1000),*ch));free.append(i)
            add([n,*flat(nodes)],'random')
    elif f==1:
        add([1,0]);add([64,64,*flat([(0,i,(i+1)%64) for i in range(64)])])
        if not smoke:
            commands=list(itertools.product(range(2),range(3),range(3)))
            for q in range(4):
                for ops in itertools.product(commands,repeat=q):add([3,q,*flat(ops)],'exhaustive')
        for _ in range(random_count):
            n=rng.randint(1,64);q=rng.randrange(65);add([n,q,*flat([(rng.randrange(2),rng.randrange(n),rng.randrange(n)) for _ in range(q)])],'random')
    elif f==2:
        add([0,0]);add([1,0]);add([0,64,*flat([(0,1000000)for _ in range(64)])]);add([1,64,*range(64)])
        if not smoke:
            for n in range(7):
                for data in itertools.product((-1,0,1),repeat=n):add([1,n,*data],'exhaustive')
            for q in range(6):
                for ops in itertools.product(((0,0),(1,0),(2,0),(3,0)),repeat=q):add([0,q,*flat(ops)],'exhaustive')
        for j in range(random_count):
            n=rng.randrange(65)
            if j%2:add([1,n,*[rng.randint(-1000000,1000000) for _ in range(n)]],'random')
            else:
                ops=[rng.randrange(4)for _ in range(n)];add([0,n,*flat([(op,rng.randint(-1000000,1000000) if op==0 else 0)for op in ops])],'random')
    elif f==3:
        for nodes,env in [([(1,0,0)],[]), ([(255,999,-999)],[]), ([(0,1,0),(0,0,0),(10,0,1)],[]),
            ([(0,-7,0),(0,3,0),(10,0,1)],[]), ([(0,1000,0)]+[(2,i-1,i-1)for i in range(1,7)],[]),
            ([(0,1,0),(1,0,0),(7,0,1)],[]), ([(0,0,0),(0,1,0),(10,1,0),(6,0,2)],[]),
            ([(0,0,0)]+[(8,i-1,0)for i in range(1,64)],[]), ([(1,7,0)],[0]*8)]:add(ast(nodes,env))
        if not smoke:
            leaves=[(0,-1,0),(0,0,0),(0,1,0),(1,0,0),(11,0,0)]
            for a,b in itertools.product(leaves,repeat=2):
                for tag in range(2,11):
                    for l,r in itertools.product(range(2),repeat=2):
                        if tag not in (8,9)or r==0:add(ast([a,b,(tag,l,r)]),'exhaustive')
        for _ in range(random_count):
            n=rng.randint(1,64);e=rng.randrange(9);env=[rng.randint(-1000,1000)for _ in range(e)];nodes=[]
            for i in range(n):
                tag=rng.choice([0,0,0,1,11,255] if i==0 else list(range(11))+[11,255])
                a=rng.randint(-1000,1000)if tag==0 or tag>10 else rng.randrange(16)if tag==1 else rng.randrange(i)
                b=rng.randint(-1000,1000)if tag>10 else rng.randrange(i)if 2<=tag<=10 and tag not in(8,9) else 0
                nodes.append((tag,a,b))
            add(ast(nodes,env),'random')
    elif f==4:
        examples=[[],[1],[0,0,0],[1,33,0],[1,2,0],[1,0,0,1],record(3,[2]),[3,1,0,1,0],record(2,[]),record(3,[1]),record(2,list(range(32)))]
        for data in examples:
            add(stream(data));add(stream(record(1,[0,255])+data))
        add(stream([2,32,0]+[0]*32+[34]+[0]*60))
        if not smoke:
            for n in range(5):
                for data in itertools.product((0,1,2,3,32,33,255),repeat=n):add(stream(list(data)),'exhaustive')
        for j in range(random_count):
            if j%3==0:data=[rng.randrange(256)for _ in range(rng.randrange(97))]
            else:
                data=[]
                for _ in range(rng.randrange(1,9)):
                    tag=rng.randint(1,3);p=[rng.randrange(256)for _ in range(2 if tag==1 else rng.randrange(12)if tag==2 else 1)]
                    if tag==3:p=[rng.randrange(2)]
                    block=record(tag,p)
                    if len(data)+len(block)<=96:data+=block
                if j%3==2 and data:
                    if j%2:data=data[:rng.randrange(len(data))]
                    else:data[rng.randrange(len(data))]=rng.randrange(256)
            add(stream(data),'random')
    elif f==5:
        for data in ([],[0],[92],[34],[39],[34,92],[34,0],[92,0],list(b'a b "" c\\'),[39,92,39],[65]*64,[34,34]*32):add(stream(data))
        if not smoke:
            for n in range(5):
                for data in itertools.product((0,9,32,34,39,65,92,255),repeat=n):add(stream(list(data)),'exhaustive')
        for j in range(random_count):
            alphabet=(0,9,32,34,39,65,66,92,255)if j%2 else tuple(range(256))
            add(stream([rng.choice(alphabet)for _ in range(rng.randrange(65))]),'random')
    elif f==6:
        for data,cap in (([],0),([128]*64,0),([0],0),([0,65],0),([255],0),([255,65],1),([0,65,0],96),([129,65],96),([128,0],96),([95]+[65]*63,96)):
            add(stream(data,cap))
        if not smoke:
            for n in range(5):
                for data in itertools.product((0,1,65,127,128,254,255),repeat=n):
                    for cap in (0,1,2,96):add(stream(list(data),cap),'exhaustive')
        for j in range(random_count):
            cap=rng.randrange(97)
            if j%3==0:data=[rng.randrange(256)for _ in range(rng.randrange(65))]
            else:
                data=[]
                for _ in range(rng.randrange(1,12)):
                    typ=rng.randrange(3)
                    if typ==0:
                        k=rng.randint(1,12);block=[k-1,*[rng.randrange(256)for _ in range(k)]]
                    elif typ==1:block=[rng.randint(129,255),rng.randrange(256)]
                    else:block=[128]
                    if len(data)+len(block)<=64:data+=block
                if j%3==2 and data:data=data[:-1]
            add(stream(data,cap),'random')
    else:
        for data in (b'',b'/',b'///',b'.',b'..',b'/../../a',b'a/../..',b'a/./b/../../',b'../a/../..',b'../..',b'a\0/..',b'/'*64,b'a'*64):add(stream(list(data)))
        if not smoke:
            for n in range(7):
                for data in itertools.product((0,46,47,65),repeat=n):add(stream(list(data)),'exhaustive')
        for j in range(random_count):
            if j%3==0:data=[rng.randrange(256)for _ in range(rng.randrange(65))]
            else:
                parts=[rng.choice([b'',b'.',b'..',b'a',b'bc',b'...',b'\xff'])for _ in range(rng.randrange(20))]
                data=list((rng.choice([b'',b'/'])+b'/'.join(parts)+rng.choice([b'',b'/']))[:64])
            add(stream(data),'random')
    return result,counts,duplicates

def invalid_cases(f):
    return {0:[[],[-1],[1,0,0,-1],[2,0,-1,-1,1,0,0],[1,1001,-1,-1]],
      1:[[],[0,0],[1,1,2,0,0],[1,1,1,0,1],[65,0]],
      2:[[],[2,0],[0,1,1,1],[1,1,1000001],[0,65]+[1,0]*65],
      3:[[],[0,0],[1,0,2,0,0],[1,0,0,1001,0],[1,9]+[0]*12,[1,0,256,0,0]],
      4:[[],[-1],[97]+[0]*97,[1,256],[2,1]],
      5:[[],[-1],[65]+[0]*65,[1,-1],[2,0]],
      6:[[],[0,-1],[0,97],[1,1,256],[2,0,0]],
      7:[[],[-1],[65]+[0]*65,[1,256],[2,1]]}[f]
