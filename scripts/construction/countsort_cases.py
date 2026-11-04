"""Bounded stable sorting corpora, with exhaustive keys and seeded records."""
from collections import Counter
from itertools import product
import random
def valid_domain(domain,x):
    return (domain==0 and bool(x) and all(type(v)is int for v in x) and 0<=x[0]<=64 and len(x)==1+2*x[0]
      and all(-3<=x[1+2*i]<=3 and -1000<=x[2+2*i]<=1000 for i in range(x[0])))
def valid(family,x):return valid_domain(family,x)
def records(items):return [len(items),*(v for item in items for v in item)]
def corpus(family,random_count,smoke):
    rng=random.Random(2026110414);cases=[];seen=set();counts=Counter();duplicates=0
    def add(x,origin):
        nonlocal duplicates
        assert valid(0,x),x;key=tuple(x)
        if key in seen:duplicates+=1
        else:seen.add(key);cases.append(x);counts[origin]+=1
    for items in ([],[(0,1),(0,2)],[(-3,1000),(3,-1000)],[(-3,i)for i in range(64)],[(i%7-3,i)for i in range(64)]):add(records(items),'boundary')
    if not smoke:
        for n in range(8):
            for keys in product((-1,0,1),repeat=n):add(records([(k,i)for i,k in enumerate(keys)]),'exhaustive')
    for _ in range(random_count):
        n=rng.randrange(65);add(records([(rng.randint(-3,3),rng.randint(-1000,1000))for _ in range(n)]),'random')
    return cases,dict(counts),duplicates
def invalid_cases(family):return [[],[-1],[1],[1,-4,0],[1,4,0],[1,0,1001],[65]+[0]*130]
def observation_features(family,x,raw):
    assert raw[0]==len(raw)-1==2*x[0]; result=list(zip(raw[1::2],raw[2::2]));source=list(zip(x[1::2],x[2::2]))
    assert result==sorted(source,key=lambda item:item[0]);out=Counter()
    if not source:out['empty']+=1
    if len(source)==64:out['max-size']+=1
    if len({k for k,_ in source})<len(source):out['equal-keys']+=1
    if any(k in (-3,3)for k,_ in source):out['boundary-key']+=1
    return out
REQUIRED_FEATURES=[{'empty','max-size','equal-keys','boundary-key'}]
