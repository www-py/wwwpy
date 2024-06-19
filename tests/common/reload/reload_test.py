
"""
Reload tests are defined like the following:
- setup initial module(s)
- verify something about the module(s)
- change the module(s)
- invoke the reload function
- verify the change(s) took effect
"""
from pathlib import Path


def test_reload__component(pytester):
    # GIVEN
    # copy all the content of test_files to the pytester path
    test_files = Path(__file__).parent / 'reload_1'
    for file in test_files.iterdir():
        if file.is_dir():
            continue
        filename = file.name.replace('_test_disable.py','_test.py')
        (pytester.path / filename).write_text(file.read_text())

    # WHEN
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
