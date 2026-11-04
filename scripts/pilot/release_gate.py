"""Fail-closed public pilot entry point until solver packages are certified.

This does not run or grade a submitted proof. It deliberately refuses every
frozen task until the redaction, binding and adversarial audits are complete.
"""
import argparse,json,re
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
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);parser.add_argument('--platform',required=True);args=parser.parse_args()
    result=decide(args.task,args.platform);print(json.dumps(result));raise SystemExit(2)
if __name__=='__main__':main()
