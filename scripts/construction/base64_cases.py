"""RFC vectors, exhaustive short byte strings and random bounded byte strings."""
from collections import Counter
from itertools import product
import json
import random
from base64_common import CORE
FIXTURES=json.loads((CORE/"fixtures.json").read_text())
def valid_domain(_family,x):
    return bool(x) and 0<=x[0]<=64 and len(x)==1+x[0] and all(0<=b<=255 for b in x[1:])
valid=valid_domain
def corpus(_family,random_count,smoke):
    rng=random.Random(2026110407)
    seen=set();cases=[];counts=Counter();duplicates=0
    def add(data,origin):
        nonlocal duplicates
        x=[len(data),*data];assert valid(0,x)
        if tuple(x) in seen:
            duplicates+=1;return
        seen.add(tuple(x));cases.append(x);counts[origin]+=1
    for word in FIXTURES["inputs"]:add(list(word.encode("ascii")),"source")
    for data in ([],[0],[255],[0]*64,[255]*64,list(range(64))):add(data,"boundary")
    if not smoke:
        for n in range(7):
            for data in product((0,1,127,255),repeat=n):add(list(data),"exhaustive")
    for _ in range(random_count):
        add([rng.randrange(256) for _ in range(rng.randrange(65))],"random")
    return cases,dict(counts),duplicates
def invalid_cases(_family):
    return [[],[-1],[1],[1,256],[1,-1],[65]+[0]*65]
def observation_features(_family,x,raw):
    assert raw[0]==len(raw)-1
    assert raw[0]==4*((x[0]+2)//3)
    assert all((65<=b<=90 or 97<=b<=122 or 48<=b<=57 or b in (43,47,61)) for b in raw[1:])
    c=Counter()
    c["empty" if x[0]==0 else "nonempty"]+=1
    c["remainder-"+str(x[0]%3)]+=1
    return c
REQUIRED_FEATURES=[{"empty","nonempty","remainder-0","remainder-1","remainder-2"}]
