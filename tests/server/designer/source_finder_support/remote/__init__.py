from pathlib import Path

from js import document, console


async def main():
    console.log('testing source_finder')
    document.body.innerHTML = 'checking...'

    from wwwpy.common.designer.source_finder import find_source_file
    from remote.FindmeComponent import FindmeComponent

    path = find_source_file(FindmeComponent)
    expected = Path(__file__).parent / 'FindmeComponent.py'
    document.body.innerHTML = 'path ok' if path == expected else f'failed {path} != {expected}'
