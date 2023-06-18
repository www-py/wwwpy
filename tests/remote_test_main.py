import os


async def install(package):
    from js import pyodide
    await pyodide.loadPackage('micropip')
    import micropip
    await micropip.install([package])


async def main():
    await install('pytest')
    await install('pytest-xvirt')
    import pytest
    print('-=-' * 20 + 'pytest imported')

    print(str(os.listdir('/wwwpy_bundle')))
    pytest.main([str("/wwwpy_bundle/remote")])
