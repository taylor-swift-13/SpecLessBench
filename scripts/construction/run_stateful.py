"""One measured envelope per implementation group, including corpus generation."""
import argparse,sys
from stateful_common import GROUPS,ROOT
from measure import measured
def main():
    p=argparse.ArgumentParser();p.add_argument('--family',choices=[g[0]for g in GROUPS]);p.add_argument('--smoke',action='store_true');a=p.parse_args()
    for name,gid,*_ in GROUPS:
        if a.family and name!=a.family:continue
        cmd=[sys.executable,str(ROOT/'scripts/construction/differential_stateful.py'),'--family',name,'--random-cases','8'if a.smoke else'10000']
        if a.smoke:cmd.append('--smoke')
        _,r=measured(cmd,gid,'smoke-differential'if a.smoke else'full-differential',role='envelope',timeout=2400)
        print(name,'passed; envelope seconds',round(r['wall_seconds'],3),flush=True)
if __name__=='__main__':main()
