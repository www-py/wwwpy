import shutil
from pathlib import Path


def _setup_quickstart(directory: Path):
    source = Path(__file__).parent / 'setup1'
    shutil.copytree(source, directory, dirs_exist_ok=True)
