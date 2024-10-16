from __future__ import annotations

import subprocess
from pathlib import Path


def uncommitted_changes():
    result = subprocess.run(['git', 'diff-index', '--quiet', 'HEAD', '--'], capture_output=True)
    present = result.returncode != 0
    if present:
        print("There are uncommitted changes. Please commit or stash them before running this script.")
        print("")
        subprocess.run(['git', 'diff-index', 'HEAD', '--'])
    return present


def write_build_meta():
    Path('src/wwwpy/_build_meta.py').write_text(
        f"""git_hash_short="{subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()}"
git_hash="{subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()}"
""")


if __name__ == '__main__':
    write_build_meta()
