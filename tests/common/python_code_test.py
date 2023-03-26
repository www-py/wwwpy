from wwwpy.common.python_code import add_exception_block


def test_python_code_execution():
    tmp = []
    code = add_exception_block('1/0', (
        'tmp.append("executed")\n'
        'tmp.append("type=" + str(type(exception).__name__))'
    ))
    exec(code)
    assert ['executed', 'type=ZeroDivisionError'] == tmp
