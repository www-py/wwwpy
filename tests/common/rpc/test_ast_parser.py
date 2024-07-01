from tests.common.rpc.test_rpc import support1_module_name
from wwwpy.common.rpc import ast_parser


def test_ast_function_len():
    target = ast_parser.module_from_package_name(support1_module_name)

    # THEN
    assert target.name == 'tests.common.rpc.support1'
    assert len(target.functions) == 2


def test_ast_module_function0():
    # WHEN
    target = ast_parser.module_from_package_name(support1_module_name)

    # THEN
    fun = target.functions[0]
    assert fun.name == 'support1_function0'
    assert fun.signature == '(a: int, b: int) -> int'
    assert not fun.is_coroutine_function


def test_ast_module_function1():
    # WHEN
    target = ast_parser.module_from_package_name(support1_module_name)

    # THEN
    fun = target.functions[1]
    assert fun.name == 'support1_function1'
    assert fun.signature == '(a: int, b: float) -> str'
    assert fun.is_coroutine_function
