"""Deterministic bounded corpora and independent input validity checks."""
from collections import Counter
from itertools import product
import random

def valid_domain(domain,x):
    if not x or any(type(v) is not int for v in x):return False
    if domain in (0,1):
        n=x[0]
        if not 1<=n<=8 or len(x)!=1+n*n:return False
        return all((0<=v<=1 if domain==1 else (v==-1 if p//n==p%n else -1<=v<=100)) for p,v in enumerate(x[1:]))
    if domain==2:
        if len(x)<2:return False
        n,m=x[:2]
        return 0<=n<=48 and 0<=m<=16 and len(x)==2+n+m and all(0<=v<=3 for v in x[2:])
    return False
def valid(family,x):return valid_domain(family,x)
def graph(n,values):return [n,*values]
def search(t,p):return [len(t),len(p),*t,*p]
def corpus(family,random_count,smoke):
    rng=random.Random(2026110411+family);cases=[];seen=set();counts=Counter();duplicates=0
    def add(x,origin):
        nonlocal duplicates
        assert valid(family,x),x
        key=tuple(x)
        if key in seen:duplicates+=1
        else:seen.add(key);cases.append(x);counts[origin]+=1
    if family==0:
        add(graph(2,[-1,0,-1,-1]),'witness')
        add(graph(1,[-1]),'boundary')
        add(graph(8,[-1]*64),'boundary')
        if not smoke:
            pairs=[(i,j)for i in range(3)for j in range(3)if i!=j]
            for ws in product((-1,0,1,2),repeat=6):
                m=[-1]*9
                for (i,j),w in zip(pairs,ws):m[3*i+j]=w
                add(graph(3,m),'exhaustive')
        for _ in range(random_count):
            n=rng.randint(1,8);m=[-1 if i==j or rng.randrange(4)==0 else rng.randrange(101) for i in range(n)for j in range(n)]
            add(graph(n,m),'random')
    elif family==1:
        add(graph(2,[0,1,0,0]),'witness');add(graph(2,[0,1,1,0]),'boundary');add(graph(1,[0]),'boundary');add(graph(8,[0]*64),'boundary')
        if not smoke:
            for bits in product((0,1),repeat=9):add(graph(3,bits),'exhaustive')
        for _ in range(random_count):
            n=rng.randint(1,8);add(graph(n,[int(rng.randrange(4)==0)for _ in range(n*n)]),'random')
    else:
        add(search([0,0,1],[0,1]),'witness');add(search([],[]),'boundary')
        add(search([3]*48,[3]*16),'boundary')
        if not smoke:
            for n in range(7):
                for t in product(range(2),repeat=n):
                    for m in range(5):
                        for p in product(range(2),repeat=m):add(search(t,p),'exhaustive')
        for _ in range(random_count):
            n=rng.randrange(49);m=rng.randrange(17)
            add(search([rng.randrange(4)for _ in range(n)],[rng.randrange(4)for _ in range(m)]),'random')
    return cases,dict(counts),duplicates
def invalid_cases(family):
    if family==0:return [[],[0],[1,0],[2,-1,0,-1,0],[2,-1,-2,-1,-1],[1,-1,0]]
    if family==1:return [[],[0],[1,2],[1,-1],[2,0,1,1,2],[1,0,1]]
    return [[],[0],[0,-1],[49,0]+[0]*49,[0,17]+[0]*17,[1,0,4],[0,0,0]]
def observation_features(family,x,raw):
    assert raw[0]==len(raw)-1;out=Counter()
    if family==0:
        n=x[0]; assert len(raw)==1+n*n
        assert all(raw[1+i*n+i]==0 for i in range(n))
        if 0 in x[1:]:out['zero-edge']+=1
        if -1 in raw[1:]:out['unreachable']+=1
        if n==8:out['max-size']+=1
    elif family==1:
        n=x[0];assert len(raw)==1+n*n
        r=raw[1:];assert all(r[i*n+i]==1 for i in range(n))
        assert all(r[i*n+j]==r[j*n+i] for i in range(n)for j in range(n))
        if any(r[i*n+j] for i in range(n)for j in range(n)if i!=j):out['nontrivial-component']+=1
        if any(not r[i*n+j] for i in range(n)for j in range(n)):out['separate-components']+=1
        if n==8:out['max-size']+=1
    else:
        assert len(raw)==2
        n,m=x[:2];idx=raw[1];text=x[2:2+n];pat=x[2+n:]
        oracle=next((i for i in range(n-m+1)if text[i:i+m]==pat),-1)
        assert idx==oracle
        if m==0:out['empty-pattern']+=1
        if n==48:out['max-text']+=1
        if idx>=0:out['match']+=1
    return out
REQUIRED_FEATURES=[{'zero-edge','unreachable','max-size'}, {'nontrivial-component','separate-components','max-size'}, {'empty-pattern','max-text','match'}]
