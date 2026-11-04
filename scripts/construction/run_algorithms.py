"""Run each implementation group's measured envelope exactly once per attempt."""
import argparse
import sys
from algorithms_common import GROUPS, ROOT
from measure import measured

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--family",choices=[g[0] for g in GROUPS])
    parser.add_argument("--smoke",action="store_true")
    args=parser.parse_args()
    for name,gid,*_ in GROUPS:
        if args.family and name!=args.family: continue
        cmd=[sys.executable,str(ROOT/"scripts/construction/differential_algorithms.py"),"--family",name,
             "--random-cases","8" if args.smoke else "5000"]
        if args.smoke: cmd.append("--smoke")
        _,record=measured(cmd,gid,"smoke-differential" if args.smoke else "full-differential",role="envelope",timeout=1800)
        print(name,"passed; envelope seconds",round(record["wall_seconds"],3),flush=True)

if __name__=="__main__": main()
