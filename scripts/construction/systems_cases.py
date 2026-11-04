"""Transport validation, deterministic corpora and observation coverage."""
from collections import Counter
from itertools import product
import json
import random

from systems_common import CORE, GROUPS

FIXTURES = json.loads((CORE / "fixtures.json").read_text())


def valid_domain(family, xs):
    if not xs:
        return False
    if family == 3:
        if len(xs) < 6:
            return False
        n, m, band, opening, extension, mismatch = xs[:6]
        return (0 <= n <= 12 and 0 <= m <= 12 and 0 <= band <= 12
                and 1 <= opening <= 10 and 0 <= extension <= opening
                and 0 <= mismatch <= 10 and len(xs) == 6+n+m
                and all(0 <= symbol <= 4 for symbol in xs[6:]))
    if family == 4:
        if len(xs) < 7:
            return False
        n, count, step, den, phase, lo, hi = xs[:7]
        return (1 <= n <= 16 and 0 <= count <= 32 and -24 <= step <= 24
                and 1 <= den <= 16 and -64 <= phase <= 128 and -512 <= lo <= hi <= 512
                and len(xs) == 7+n and all(-512 <= x <= 512 for x in xs[7:]))
    q = xs[0]
    if not (0 <= q <= 64 and len(xs) == 1+4*q):
        return False
    for p in range(1, len(xs), 4):
        op, a, b, c = xs[p:p+4]
        if family == 0:
            ok = 0 <= op <= 4 and 0 <= a <= 7 and c == 0 and (0 <= b <= 7 if op <= 1 else b == 0)
        elif family == 1:
            ok = (0 <= op <= 4 and c == 0 and (0 <= a <= 7 if op <= 2 else a == 0)
                  and (-1000 <= b <= 1000 if op == 0 else b == 0))
        else:
            ok = (0 <= op <= 3 and 0 <= a <= (4 if op == 3 else 7)
                  and (-1000 <= b <= 1000 and 1 <= c <= 8 if op == 0 else b == c == 0))
        if not ok:
            return False
    return True


valid = valid_domain


def trace(ops):
    return [len(ops), *(word for op in ops for word in op)]


def command(op, a=0, b=0, c=0):
    return op, a, b, c


def alignment(a, b, band=12, opening=2, extension=1, mismatch=2):
    return [len(a), len(b), band, opening, extension, mismatch, *a, *b]


def resample(samples, count=12, step=1, den=2, phase=0, lo=-512, hi=512):
    return [len(samples), count, step, den, phase, lo, hi, *samples]


def history_seeds(family):
    c = command
    if family == 0:
        return [
            [c(0,0,1),c(2,0),c(0,1,2),c(2,0),c(4,2)],
            [*(c(0,i,i-1) for i in range(7,0,-1)),c(0,0,7),c(2,7),c(3,4),c(2,7)],
            [c(0,0,0),c(0,0,1),c(0,1,2),c(0,2,0),c(2),c(1,1,2),c(3,2),c(2)],
        ]
    if family == 1:
        return [
            [c(0,0,19),c(3),c(1),c(2),c(4),c(2)],
            [c(4),c(0,7,-1000),*[c(3)]*5,c(2,7),c(1,7),c(2,7),c(4),c(2,7)],
        ]
    return [
        [c(0,0,10,1),c(0,0,20,2),c(3,1),c(1)],
        [c(3,4),c(3,4),c(0,3,-1000,1),c(0,7,1000,1),c(3,0),c(3,1)],
        [c(0,1,1,8),c(2,1),c(0,1,2,1),c(3,1),c(3,4),c(3,4),c(1,1)],
    ]


def corpus(family, random_count, smoke):
    cases, seen, counts = [], set(), Counter()
    duplicates = 0
    rng = random.Random(2026110406+family)
    c = command

    def add(xs, origin):
        nonlocal duplicates
        assert valid(family, xs), xs
        key = tuple(xs)
        if key in seen:
            duplicates += 1
            return
        seen.add(key)
        cases.append(xs)
        counts[origin] += 1

    fixture = FIXTURES.get(GROUPS[family][0], {})
    for xs in fixture.get("inputs", []):
        add(xs, "source")
    if family < 3:
        add(trace([]), "boundary")
        seeds = history_seeds(family)
        for ops in seeds:
            add(trace(ops), "boundary")
            add(trace((ops*64)[:64]), "stress")
        alphabets = [
            [c(0,0,1),c(0,1,2),c(0,2,0),c(1,0,1),c(2),c(2,1),c(3,2),c(4,2)],
            [c(0,0,1),c(0,1,-1),c(1),c(2),c(2,1),c(3),c(4)],
            [c(0,0,1,1),c(0,0,2,2),c(0,1,3,1),c(1),c(2),c(3,1),c(3,2)],
        ]
        if not smoke:
            for length in range(5):
                for ops in product(alphabets[family], repeat=length):
                    add(trace(ops), "exhaustive")
            if family == 0:
                for a,b,d in product(range(8), repeat=3):
                    add(trace([c(0,a,b),c(2,a),c(0,b,d),c(3,d),c(2,a),c(4,d)]), "structured")
            elif family == 1:
                for key,depth,value in product(range(8),range(1,5),(-1000,-1,0,1,1000)):
                    ops = [c(0,key,value),*[c(3)]*depth,c(1,key),c(2,key),
                           *[c(4)]*depth,c(2,key)]
                    add(trace(ops), "structured")
            else:
                for shift,key,first,second in product(range(9),range(8),range(1,9),range(1,9)):
                    advance = [c(3,1)]*shift
                    ops = [*advance,c(0,key,-1,first),c(0,key,2,second),
                           *[c(3,1)]*first,c(1,key),*[c(3,1)]*(max(0,second-first)),c(1,key)]
                    add(trace(ops), "structured")
        for trial in range(random_count):
            q = rng.randrange(65)
            ops = []
            for _ in range(q):
                if family == 0:
                    op = rng.choice((0,0,0,1,2,2,3,4))
                    ops.append(c(op,rng.randrange(8),rng.randrange(8) if op <= 1 else 0))
                elif family == 1:
                    op = rng.choice((0,0,1,2,2,3,4))
                    ops.append(c(op,rng.randrange(3 if trial%2 else 8) if op <= 2 else 0,
                                 rng.randint(-1000,1000) if op == 0 else 0))
                else:
                    op = rng.choice((0,0,0,1,2,3,3))
                    a = rng.randrange(5 if op == 3 else (2 if trial%2 else 8))
                    ops.append(c(op,a,rng.randint(-1000,1000) if op == 0 else 0,
                                 rng.randint(1,8) if op == 0 else 0))
            add(trace(ops), "random")
    elif family == 3:
        for xs in (
            alignment([0],[1],1,1,0,1), alignment([],[]), alignment([0],[],0),
            alignment([4],[2],0), alignment([0]*12,[1]*12,12,1,0,10),
            alignment([0]*12,[],12,10,10,10), alignment([0,1],[1,0],0),
        ):
            add(xs, "boundary")
        if not smoke:
            seqs = [s for n in range(4) for s in product((0,1,4), repeat=n)]
            for a,b,(band,opening,extension,mismatch) in product(
                seqs,seqs,((0,1,0,1),(1,1,0,1),(2,2,1,2),(12,4,2,5))
            ):
                add(alignment(a,b,band,opening,extension,mismatch), "exhaustive")
        for _ in range(random_count):
            a = [rng.randrange(5) for _ in range(rng.randrange(13))]
            b = [rng.randrange(5) for _ in range(rng.randrange(13))]
            opening = rng.randint(1,10)
            add(alignment(a,b,rng.randrange(13),opening,rng.randrange(opening+1),rng.randrange(11)), "random")
    else:
        for xs in (
            resample([-1,0],1,0,2,1), resample([0,1],1,0,2,1),
            resample([-500,500],8,1,2,-2,-200,200),
            resample([5],0), resample([1,-1],32,-24,1,128),
        ):
            add(xs, "boundary")
        for step in (-7,-1,0,1,3,7):
            for den in (2,3,8,16):
                phase = 15*den if step < 0 else -1
                if phase > 128:
                    phase = 128
                add(resample(fixture["samples"],32,step,den,phase,110,145), "source")
        if not smoke:
            for a,b,den,phase,step in product(range(-3,4),range(-3,4),range(1,7),range(-2,8),(-3,0,3)):
                add(resample([a,b],5,step,den,phase,-2,2), "exhaustive")
        for _ in range(random_count):
            samples = [rng.randint(-512,512) for _ in range(rng.randint(1,16))]
            lo,hi = sorted((rng.randint(-512,512),rng.randint(-512,512)))
            add(resample(samples,rng.randrange(33),rng.randint(-24,24),rng.randint(1,16),
                         rng.randint(-64,128),lo,hi), "random")
    return cases, dict(counts), duplicates


def invalid_cases(family):
    examples = [
        [trace([command(0,8)]),trace([command(3,0,1)])],
        [trace([command(3,1)]),trace([command(0,1,1001)])],
        [trace([command(0,1,1,0)]),trace([command(3,5)])],
        [alignment([5],[]),alignment([0],[1],0,1,2),[0,0,13,1,0,0]],
        [resample([],0),resample([0],den=0),resample([0],lo=1,hi=-1)],
    ]
    return [[],[-1],[1],*examples[family]]


REQUIRED_FEATURES = [
    {"multi-node-propagation","repeat-dirty-root","clear-dirty","edge-edit-after-dirty"},
    {"base-pop","depth-limit","deep-hit","inner-miss","restored-hit"},
    {"refresh","multi-expiry","advance-zero","wheel-wrap"},
    {"unreachable","tie-mask","empty-pair","wildcard"},
    {"left-edge","right-edge","low-saturation","high-saturation","negative-step","empty-output"},
]


def observation_features(family, xs, raw):
    length, *out = raw
    assert length == len(out)
    events = Counter()
    if family == 0:
        assert len(out) == 3*xs[0]
        dirty = 0
        for i in range(xs[0]):
            op, result, after = out[3*i:3*i+3]
            assert op == xs[1+4*i] and result in (0,1) and 0 <= after < 256
            a = xs[2+4*i]
            if op == 2 and (after & ~dirty).bit_count() >= 2:
                events["multi-node-propagation"] += 1
            if op == 2 and dirty & (1 << a):
                events["repeat-dirty-root"] += 1
            if op == 3 and after != dirty:
                events["clear-dirty"] += 1
            if op <= 1 and dirty:
                events["edge-edit-after-dirty"] += 1
            dirty = after
    elif family == 1:
        assert len(out) == 5*xs[0]+16
        previous = -1
        for i in range(xs[0]):
            op,status,found,value,depth = out[5*i:5*i+5]
            assert op == xs[1+4*i] and status in (0,1,2) and found in (0,1) and 0 <= depth <= 4
            assert -1000 <= value <= 1000
            if op == 4 and status == 1:
                events["base-pop"] += 1
            if op == 3 and status == 2:
                events["depth-limit"] += 1
            if op == 2 and depth == 4 and found:
                events["deep-hit"] += 1
            if op == 2 and depth and not found:
                events["inner-miss"] += 1
            if op == 2 and previous == 4 and found:
                events["restored-hit"] += 1
            previous = op
    elif family == 2:
        index = clock = 0
        live = set()
        for i in range(xs[0]):
            op,found,value,count = out[index:index+4]
            assert op == xs[1+4*i] and found in (0,1) and -1000 <= value <= 1000 and 0 <= count <= 8
            keys = out[index+4:index+4+count]
            assert len(set(keys)) == count and all(0 <= key < 8 for key in keys)
            a = xs[2+4*i]
            if op == 0:
                events["refresh"] += int(a in live)
                live.add(a)
            if op == 2:
                live.discard(a)
            if op == 3:
                if count > 1:
                    events["multi-expiry"] += 1
                if a == 0:
                    events["advance-zero"] += 1
                if clock//9 != (clock+a)//9:
                    events["wheel-wrap"] += 1
                clock += a
                live.difference_update(keys)
            index += 4+count
        assert len(out)-index == 17 and out[index] == clock
    elif family == 3:
        score,mask = out
        assert -1 <= score <= 240 and 0 <= mask <= 7
        if score == -1:
            events["unreachable"] += 1
        if mask.bit_count() > 1:
            events["tie-mask"] += 1
        if xs[:2] == [0,0]:
            events["empty-pair"] += 1
        if 4 in xs[6:]:
            events["wildcard"] += 1
    else:
        assert len(out) == 3*xs[1]
        if not out:
            events["empty-output"] += 1
        if xs[2] < 0:
            events["negative-step"] += 1
        for i in range(0,len(out),3):
            value,edge,saturation = out[i:i+3]
            assert xs[5] <= value <= xs[6] and edge in (-1,0,1) and saturation in (-1,0,1)
            if edge != 0:
                events["left-edge" if edge < 0 else "right-edge"] += 1
            if saturation != 0:
                events["low-saturation" if saturation < 0 else "high-saturation"] += 1
    return +events
