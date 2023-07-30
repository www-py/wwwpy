import os


async def install(package):
    from js import pyodide
    await pyodide.loadPackage('micropip')
    import micropip
    await micropip.install([package])


async def main(rootpath, invocation_dir, args):
    await install('pytest')
    await install('pytest-xvirt')
    import pytest
    print('-=-' * 20 + 'pytest imported')

    from wwwpy.common.tree import print_tree
    print_tree('/wwwpy_bundle')

    os.chdir(invocation_dir)
    pytest.main(args)
