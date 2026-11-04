"""Private curator storage lives on WSL's permission-enforcing filesystem."""
from pathlib import Path
PRIVATE=Path.home()/'.local/share/speclessbench/pilot-v1'
