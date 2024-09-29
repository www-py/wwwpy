import shutil
from pathlib import Path


def _setup_quickstart(directory: Path):
    source = Path(__file__).parent / 'setup1'
    shutil.copytree(source, directory, dirs_exist_ok=True)


def _check_quickstart(directory: Path):
    if _do_quickstart(directory):
        print(f'empty directory, creating quickstart in {directory.absolute()}')
        _setup_quickstart(directory)
    else:
        (directory / 'remote').mkdir(exist_ok=True)


def _do_quickstart(directory):
    return all(item.name.startswith('.') for item in directory.iterdir())