"""Read this process's cgroup v2 limits; no persistent system change."""
import json
from pathlib import Path
line=next(s for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::'))
p=Path('/sys/fs/cgroup')/line[3:].lstrip('/')
print(json.dumps({'cgroup':line[3:],'memory_max':(p/'memory.max').read_text().strip(),
                  'pids_max':(p/'pids.max').read_text().strip(),
                  'memory_swap_max':(p/'memory.swap.max').read_text().strip()}))
