import textwrap


def indent_code(code: str, times=1) -> str:
    return textwrap.indent(code, ' ' * (4 * times))
