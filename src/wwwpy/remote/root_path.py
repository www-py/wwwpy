from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from js import console

from wwwpy.common import modlib


@dataclass
class _Dir:
    root: Path
    remote: Path


def _get_dir():
    # this works because both wwwpy and user code are flattened in the same folder
    root = modlib._find_module_path('wwwpy').parent.parent
    console.log(f'root={root}')
    remote = root / 'remote'
    return _Dir(root, remote)
