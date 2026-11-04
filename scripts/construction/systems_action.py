"""Measure metadata/curation actions in this batch as well as compiler runs."""
import sys
from pathlib import Path
from systems_common import ROOT
from measure import measured
def main():
    target=(ROOT/sys.argv[1]).resolve()
    assert target.is_relative_to((ROOT/'scripts').resolve())and target.is_file()
    out,_=measured([sys.executable,str(target),*sys.argv[2:]],'shared-systems-audit',target.stem,role='envelope',timeout=1800)
    print(out.decode(),end='')
if __name__=='__main__':main()
