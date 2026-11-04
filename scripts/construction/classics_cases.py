"""Small exhaustive and seeded random graphs and record sequences."""
from collections import Counter
from itertools import combinations, product
import random

def valid_domain(domain, x):
    if not x:
        return False
    if domain==2:
        return (0<=x[0]<=64 and len(x)==1+2*x[0]
                and all(-1000<=v<=1000 for v in x[1:]))
    if len(x)<3 or x[0]!=domain:
        return False
    mode,n,m=x[:3]
    if not (1<=n<=8 and 0<=m<=28 and len(x)==3+3*m):
        return False
    edges=[tuple(x[3+3*i:6+3*i]) for i in range(m)]
    return (all(0<=u<v<n and -1000<=w<=1000 for u,v,w in edges)
            and len({(u,v) for u,v,_ in edges})==m
            and (domain!=1 or len({w for _,_,w in edges})==m))

def valid(family,x):
    return valid_domain(x[0] if family==0 and x and x[0] in (0,1) else 2 if family==1 else 0,x)

def graph(mode,n,edges):
    return [mode,n,len(edges),*(v for edge in edges for v in edge)]

def records(items):
    return [len(items),*(v for item in items for v in item)]

def corpus(family,random_count,smoke):
    rng=random.Random(2026110408+family)
    cases=[];seen=set();counts=Counter();duplicates=0
    def add(x,origin):
        nonlocal duplicates
        assert valid(family,x),x
        key=tuple(x)
        if key in seen:
            duplicates+=1
        else:
            seen.add(key);cases.append(x);counts[origin]+=1
    if family==0:
        for mode in (0,1):
            for n,edges in [(1,[]),(4,[]),(3,[(0,1,1),(1,2,2),(0,2,3)]),
                            (8,[(i,i+1,i-4) for i in range(7)])]:
                add(graph(mode,n,edges),"boundary")
        add(graph(0,3,[(0,1,1),(1,2,1),(0,2,2)]),"witness")
        add(graph(0,3,[(0,1,1),(1,2,1),(0,2,1)]),"boundary")
        if not smoke:
            pairs=list(combinations(range(4),2))
            for values in product((None,-1,0,1),repeat=len(pairs)):
                edges=[(*pair,w) for pair,w in zip(pairs,values) if w is not None]
                add(graph(0,4,edges),"exhaustive")
                if len({w for _,_,w in edges})==len(edges):
                    add(graph(1,4,edges),"exhaustive")
        for _ in range(random_count):
            n=rng.randint(1,8);pairs=list(combinations(range(n),2));rng.shuffle(pairs)
            pairs=pairs[:rng.randrange(len(pairs)+1)];mode=rng.randrange(2)
            weights=rng.sample(range(-1000,1001),len(pairs)) if mode else [rng.randint(-3,3) for _ in pairs]
            add(graph(mode,n,[(*pair,w) for pair,w in zip(pairs,weights)]),"random")
    else:
        for items in ([],[(1,0)],[(-1000,1000)]*64,[(1,1),(1,2),(0,3)],
                      [(i%3,i) for i in range(64)],[(64-i,i) for i in range(64)]):
            add(records(items),"boundary")
        if not smoke:
            for n in range(8):
                for keys in product((-1,0,1),repeat=n):
                    add(records([(key,i) for i,key in enumerate(keys)]),"exhaustive")
        for _ in range(random_count):
            n=rng.randrange(65)
            add(records([(rng.randint(-5,5),rng.randint(-1000,1000)) for _ in range(n)]),"random")
    return cases,dict(counts),duplicates

def invalid_cases(family):
    if family==0:
        return [[],[0,0,0],[2,1,0],[2,0,0,0,0],[0,2,1,1,0,5],[0,2,2,0,1,1,0,1,2],[1,3,2,0,1,1,1,2,1]]
    return [[],[-1],[1],[1,1001,0],[1,0,-1001],[65]+[0]*130]

def observation_features(family,x,raw):
    assert raw[0]==len(raw)-1
    out=Counter()
    if family==0:
        assert len(raw)==(4 if x[0]==1 else 3)
        assert 1<=raw[2]<=x[1]
        out["unique" if x[0] else "ties-allowed"]+=1
        if raw[2]>1:out["disconnected"]+=1
        weights=x[5::3]
        if len(weights)!=len(set(weights)):out["equal-weights"]+=1
    else:
        assert len(raw)==1+2*x[0]
        result=list(zip(raw[1::2],raw[2::2]))
        assert all(result[i][0]<=result[i+1][0] for i in range(len(result)-1))
        assert sorted(result)==sorted(zip(x[1::2],x[2::2]))
        if len({key for key,_ in result})<len(result):out["duplicate-keys"]+=1
        if not result:out["empty"]+=1
        if len(result)==64:out["max-length"]+=1
    return out
REQUIRED_FEATURES=[{"unique","ties-allowed","disconnected","equal-weights"},{"duplicate-keys","empty","max-length"}]
