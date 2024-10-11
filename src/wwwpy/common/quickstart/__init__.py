import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List

from wwwpy.common.designer.element_library import NamedListMap


def _setup_quickstart(directory: Path):
    source = Path(__file__).parent / 'basic'
    shutil.copytree(source, directory, dirs_exist_ok=True)


def _check_quickstart(directory: Path):
    if _do_quickstart(directory):
        print(f'empty directory, creating quickstart in {directory.absolute()}')
        _setup_quickstart(directory)
    else:
        (directory / 'remote').mkdir(exist_ok=True)


def _do_quickstart(directory):
    return all(item.name.startswith('.') for item in directory.iterdir())


@dataclass
class Quickstart:
    name: str
    title: str
    description: str


def quickstart_list() -> NamedListMap[Quickstart]:
    source = Path(__file__).parent
    # keep only files that contains a file called 'readme.txt'
    quickstarts = []

    def add(name: str, readme: Path):
        if not readme.exists():
            return
        lines = readme.read_text().splitlines()
        title = lines[0]
        description = '\n'.join(lines[2:])
        quickstart = Quickstart(name, title, description)
        quickstarts.append(quickstart)

    for d in source.iterdir():
        if d.is_dir() and not d.name.startswith('.'):
            add(d.name, d / 'readme.txt')

    return NamedListMap(quickstarts)
