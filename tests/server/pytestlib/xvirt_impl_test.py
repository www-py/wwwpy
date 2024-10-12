import os
import shutil
import sys

import pytest

# todo, incomplete, slow and difficult to setup
def disabled_test_user_folders(pytester: pytest.Pytester):
    """Create remote package and verify that it is loaded by the browser"""
    src = os.environ['OLDPWD'] + '/.cache/ms-playwright'
    dst = os.path.expanduser('~/.cache/ms-playwright')
    shutil.copytree(src, dst)
    tr = pytester.mkpydir('tests')
    sys.path.insert(0, str(pytester.path))
    print(f'tr: {tr}')
    tr = pytester.mkpydir('tests/remote')
    (tr / 'some_test.py').write_text('def test_1(): pass')

    result = pytester.runpytest('--headful')

    # THEN
    result.assert_outcomes(passed=1, failed=0)
