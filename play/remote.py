from pathlib import Path

from js import console, document


async def main():
    await install('pytest', 'pytest-html')
    import pytest
    result = pytest.main(['--pyargs', 'play', '--html=/tmp/report.html', '--self-contained-html'])
    document.body.innerText = 'result=' + str(result)
    document.open()
    document.write(Path('/tmp/report.html').read_text())
    document.close()


async def install(*packages):
    import pyodide_js
    await pyodide_js.loadPackage('micropip')
    import micropip
    await micropip.install(packages)
