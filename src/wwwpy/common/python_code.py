import textwrap


def add_exception_block(code: str, exception_block: str) -> str:
    """It will wrap the code in try/except and catch `Exception as exception`"""
    result = 'try:\n' + textwrap.indent(code, ' ' * 4) + '\n' + \
             'except Exception as exception:\n' + textwrap.indent(exception_block, ' ' * 4)
    return result


# language=python
_try_except = """
try:
    pass # 1
except Exception as ex:
    pass # 2            
"""
