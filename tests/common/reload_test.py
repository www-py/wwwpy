
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
    content = Path(__file__).parent / 'reload_1.py'
    (pytester.path / 'reload_1_test.py').write_text(content.read_text())

    # WHEN
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)
