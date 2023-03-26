import tempfile
from pathlib import Path

from wwwpy.common.python_code import add_exception_block


def test_python_code_execution():
    tmp = tempfile.NamedTemporaryFile()
    code = add_exception_block('1/0', (
        'from pathlib import Path\n'
        'Path(tmp.name).write_text("type=" + str(type(exception).__name__))'
    ))
    exec(code)
    assert 'type=ZeroDivisionError' in Path(tmp.name).read_text()
