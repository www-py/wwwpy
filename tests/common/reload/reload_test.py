"""
Reload tests are defined like the following:
- setup initial module(s)
- verify something about the module(s)
- change the module(s)
- invoke the reload function
- verify the change(s) took effect
"""
from pathlib import Path


def test_reload_1(pytester):
    # GIVEN
    # copy all the content of test_files to the pytester path
    test_files = Path(__file__).parent / 'reload_1'
    _copy(test_files, pytester)

    # WHEN
    result = pytester.runpytest('-p', 'no:wwwpy')
    result.assert_outcomes(passed=1)


def test_reload_2(pytester):
    """Class A uses class B. When class A is reloaded, class B should be reloaded as well."""
    # GIVEN
    # copy all the content of test_files to the pytester path
    test_files = Path(__file__).parent / 'reload_2'
    _copy(test_files, pytester)

    # WHEN
    result = pytester.runpytest('-p', 'no:wwwpy')
    result.assert_outcomes(passed=1)


_ignore = {'__pycache__'}


def _copy(test_files, pytester, subpath: str = ''):
    for file in test_files.iterdir():
        if file.is_dir():
            if file.name not in _ignore:
                _copy(file, pytester, file.name + '/')
            continue
        filename = file.name.replace('_test_disable.py', '_test.py')
        path = pytester.path / (subpath + filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file.read_text())
