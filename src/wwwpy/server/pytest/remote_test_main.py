import os


async def install(package):
    from js import pyodide
    await pyodide.loadPackage('micropip')
    import micropip
    await micropip.install([package])


async def main(rootpath, invocation_dir, args):
    # Path('/wwwpy_bundle/pytest.ini').write_text("[pytest]\n"
    #                                             "asyncio_mode = auto")
    await install('pytest==7.2.2')  # didn't work with update to 8.1.1
    await install('pytest-asyncio')
    await install('pytest-xvirt')
    await install('libcst==1.3.1')
    import pytest
    print('-=-' * 20 + 'pytest imported')

    from wwwpy.common.tree import print_tree
    print_tree('/wwwpy_bundle')

    os.chdir(invocation_dir)
    pytest.main(args)
