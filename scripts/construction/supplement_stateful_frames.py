"""Novel deterministic multi-frame cases using the unchanged differential driver.

Only the corpus-provider function is injected. Programs, transport predicates,
wire format, runner commands and comparison logic remain unchanged. The main
report is restored byte-for-byte; supplemental evidence is saved separately.
"""
import gzip,hashlib,itertools,json,sys
from pathlib import Path
from stateful_common import CORE,ROOT
from stateful_cases import feed,control,trace,frame,valid
import differential_stateful as driver

def main():
    report_path=CORE/'evidence/frames.json';original=report_path.read_bytes();base=json.loads(original)
    with gzip.open(ROOT/base['corpus'],'rt')as stream:prior={tuple(json.loads(s))for s in stream}
    cases=[];seen=set();excluded=0
    def add(ops):
        nonlocal excluded
        x=trace(ops);assert valid(0,x)
        key=tuple(x)
        if key in prior or key in seen:excluded+=1;return
        seen.add(key);cases.append(x)
    for shift in range(32):
        before=[feed(frame(1,[]))]*shift
        for a,b in itertools.product(range(1,4),repeat=2):
            for payload in ([],[0],[255]):
                packed=frame(a,payload)+frame(b,[])
                add(before+[feed(packed),control(1)])
                for error in ([0],[1,9],[2,0,0],[1]):
                    chunk=frame(a,payload)+error
                    if len(chunk)<=8:add(before+[feed(chunk),control(1)])
        for a,b,c in itertools.product(range(1,4),repeat=3):
            long=frame(a,[shift%256]*8)
            for split in (9,10):
                start=[feed(long[:8]),feed(long[8:split])]
                end=long[split:]+frame(b,[])+frame(c,[])
                assert len(end)<=8
                add(before+start+[feed(end),control(1)])
        add(before+[feed([1]),feed(),control(1)])
        add(before+[feed([0]),control(2),feed(frame(3,[])),control(1)])
    assert cases
    def provider(f,random_count,smoke):
        assert f==0 and random_count==0 and not smoke
        return cases,{'structured-multiframe':len(cases)},excluded
    driver.corpus=provider
    sys.argv=[str(Path(__file__)),'--family','frames','--random-cases','0']
    status='failed'
    try:
        driver.main();status='passed'
    finally:
        produced=json.loads(report_path.read_text())if report_path.read_bytes()!=original else None
        if produced is not None:
            produced.update(supplement='structured-multiframe',provider_override={'path':Path(__file__).relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
              base_corpus_sha256=base['corpus_sha256'],novel_against_main_corpus=True,rng_seed=None,
              sampling='deterministic structured enumeration over ring residues, partial frame cuts and post-prefix errors',supplement_status=status)
            (CORE/'evidence/frames-multiframe.json').write_text(json.dumps(produced,indent=2)+'\n')
        report_path.write_bytes(original)
    print(json.dumps({'novel_inputs':len(cases),'excluded_duplicates':excluded,'status':status}))
if __name__=='__main__':main()
