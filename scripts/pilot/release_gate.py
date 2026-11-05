"""Score prepared pilot tasks; refuse all tasks that are not packaged yet."""
import argparse,contextlib,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot'
def decide(task,platform):
    manifest=json.loads((P/'manifest.json').read_text())
    if platform not in ('lean','rocq','compcert'):return {'status':'invalid-request'}
    if not re.fullmatch(r'P-[0-9a-f]{16}',task) or task not in {x['pilot_id']for x in manifest['contexts']}:
        return {'status':'unknown-task'}
    # No actual package is certified yet. Never silently fall back to the
    # original source tree or to a permissive toy checker.
    return {'status':'unavailable','reason':'solver package and evaluator are not certified'}

def score(task,platform,proof,trace=None,purpose='evaluation'):
    base=decide(task,platform)
    if base['status']!='unavailable':return base
    if purpose not in ('evaluation','reference'):return {'status':'invalid-request'}
    try:
        from selection import selection
        eligible,reference=selection()
        if purpose=='evaluation' and task in {x['pilot_id'] for x in reference}:
            return {'status':'reference-only','reason':'this entire family is excluded from evaluation'}
    except (OSError,ValueError,KeyError):return {'status':'infrastructure-error','detail':'evaluation policy failed'}
    try:
        from grade_sealed import grade
        from single_task_runner import tree_digest
        from verify_freeze import main as verify
        for name in ('first-real-task','factorial-cex'):
            build=ROOT/'_build/pilot-v1'/name;registry=build/'registry.json'
            if not registry.is_file():continue
            meta=json.loads(registry.read_text())
            if (task,platform)!=(meta['pilot_id'],meta['platform']):continue
            if meta['claim'] not in ('equivalence','counterexample') or meta['binding']!='lean-kernel-checked-correspondence':return base
            with contextlib.redirect_stdout(io.StringIO()):verify()
            if tree_digest(build/'grader')!=meta['frozen_binding_dependency_sha256']:
                return {'status':'infrastructure-error','detail':'frozen binding dependencies changed'}
            return grade(platform,build/'task',meta['public_sha256'],proof,trace=trace)
        return base
    except (OSError,ValueError,AssertionError,KeyError,json.JSONDecodeError):
        return {'status':'infrastructure-error','detail':'task verification failed'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--platform',required=True);parser.add_argument('--proof');parser.add_argument('--reference',action='store_true');args=parser.parse_args()
    result=score(args.task,args.platform,args.proof,purpose='reference' if args.reference else 'evaluation') if args.proof else decide(args.task,args.platform)
    print(json.dumps(result,sort_keys=True));raise SystemExit(0 if result['status']=='accepted' else 2)
if __name__=='__main__':main()
