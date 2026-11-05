"""Score prepared pilot tasks; refuse all tasks that are not packaged yet."""
import argparse,contextlib,io,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'benchmarks/pilot-v1'
def decide(task,platform):
    manifest=json.loads((P/'manifest.json').read_text())
    if platform not in ('lean','rocq','compcert'):return {'status':'invalid-request'}
    if not re.fullmatch(r'P-[0-9a-f]{16}',task) or task not in {x['pilot_id']for x in manifest['contexts']}:
        return {'status':'unknown-task'}
    # No actual package is certified yet. Never silently fall back to the
    # original source tree or to a permissive toy checker.
    return {'status':'unavailable','reason':'solver package and evaluator are not certified'}

def score(task,platform,proof):
    base=decide(task,platform)
    if base['status']!='unavailable':return base
    build=ROOT/'_build/pilot-v1/first-real-task';registry=build/'registry.json'
    if not registry.is_file():return base
    try:
        from grade_sealed import grade
        from single_task_runner import tree_digest
        from verify_freeze import main as verify
        meta=json.loads(registry.read_text())
        if (task,platform)!=(meta['pilot_id'],meta['platform']):return base
        if meta['claim']!='equivalence' or meta['binding']!='lean-kernel-checked-correspondence':return base
        with contextlib.redirect_stdout(io.StringIO()):verify()
        if tree_digest(build/'grader')!=meta['frozen_binding_dependency_sha256']:
            return {'status':'infrastructure-error','detail':'frozen binding dependencies changed'}
        return grade(platform,build/'task',meta['public_sha256'],proof)
    except (OSError,ValueError,AssertionError,KeyError,json.JSONDecodeError):
        return {'status':'infrastructure-error','detail':'task verification failed'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--platform',required=True);parser.add_argument('--proof');args=parser.parse_args()
    result=score(args.task,args.platform,args.proof) if args.proof else decide(args.task,args.platform)
    print(json.dumps(result,sort_keys=True));raise SystemExit(0 if result['status']=='accepted' else 2)
if __name__=='__main__':main()
