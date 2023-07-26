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

    from wwwpy.common.tree import print_tree
    print_tree('/wwwpy_bundle')

    # pytest.main([str("/wwwpy_bundle/tests/remote/test_in_pyodide_bis.py::test_bis_first")])

    os.chdir('#xvirt_pytest_invocation_dir_marker#')
    # the following line will be replaced by a python list
    pytest.main(  # xvirt_pytest_args_marker#)
    # pytest.main([str("/wwwpy_bundle/tests/remote/test_in_pyodide_bis.py")])
    # pytest.main([str("/wwwpy_bundle/tests/remote")])
