"""Copy pilot curator files to a private WSL home directory; do not delete source."""
import hashlib,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'benchmarks/pilot-v1/curator').resolve(strict=True)
assert source==(ROOT.resolve()/'benchmarks/pilot-v1/curator') and source.is_dir()
home=Path.home().resolve(strict=True);parent=home/'.local/share/speclessbench';destination=parent/'pilot-v1'
assert destination.is_relative_to(home) and not destination.exists()
parent.mkdir(parents=True,exist_ok=True,mode=0o700);destination.mkdir(mode=0o700)
files=0
for item in source.rglob('*'):
    assert not item.is_symlink(),item
    relative=item.relative_to(source);target=destination/relative
    if item.is_dir():target.mkdir(mode=0o700,exist_ok=True)
    elif item.is_file():
        target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        shutil.copyfile(item,target);os.chmod(target,0o600)
        assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(item.read_bytes()).digest(),relative
        files+=1
assert (destination.stat().st_mode & 0o077)==0
print('Copied and verified',files,'private pilot files into a mode-0700 WSL user directory; original retained pending validation.')
