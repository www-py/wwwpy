from __future__ import annotations

import subprocess


def uncommitted_changes():
    result = subprocess.run(['git', 'diff-index', '--quiet', 'HEAD', '--'], capture_output=True)
    present = result.returncode != 0
    if present:
        print("There are uncommitted changes. Please commit or stash them before running this script.")
        print("")
        subprocess.run(['git', 'diff-index', 'HEAD', '--'])
    return present
