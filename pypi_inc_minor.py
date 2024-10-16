from __future__ import annotations

import re
import subprocess

from pypi_helper import uncommitted_changes


def update_minor_version() -> str | None:
    filename = 'pyproject.toml'
    with open(filename, 'r') as f:
        lines = f.readlines()
    msg = None
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if stripped_line.startswith('version ='):
            # Use regex to extract the version string
            match = re.match(r'version\s*=\s*"(.*?)"', stripped_line)
            if match:
                version = match.group(1)
                version_parts = version.split('.')
                if version_parts[-1].isdigit():
                    # Increment the minor version
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                    new_version = '.'.join(version_parts)
                    # Replace the line with the updated version
                    lines[i] = f'version = "{new_version}"\n'
                    msg = f'Updated version to {new_version}'
                    break
                else:
                    print('Error: Last part of the version is not a digit.')
            else:
                print('Error: Could not parse the version string.')
                break
    else:
        print('Error: Version line not found.')

    if msg:
        with open(filename, 'w') as f:
            f.writelines(lines)
    return msg


def main():
    if uncommitted_changes():
        return

    msg = update_minor_version()
    if msg:
        print('=== committing changes')
        subprocess.run(['git', 'commit', '-am', msg])


if __name__ == '__main__':
    main()
