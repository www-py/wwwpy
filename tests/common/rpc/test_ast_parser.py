from __future__ import annotations

import ast

from tests.common.rpc.test_rpc import support1_module_name
from wwwpy.common.rpc import func_registry


def test_ast_function_len():
    target = func_registry.from_package_name(support1_module_name)

    # THEN
    assert target.name == 'tests.common.rpc.support1'
    assert len(target.functions) == 2


def test_ast_module_function0():
    # WHEN
    target = func_registry.from_package_name(support1_module_name)

    # THEN
    fun = target.functions[0]
    assert fun.name == 'support1_function0'
    assert fun.signature == '(a: int, b: int) -> int'
    assert not fun.is_coroutine_function


def test_ast_module_function1():
    # WHEN
    target = func_registry.from_package_name(support1_module_name)

    # THEN
    fun = target.functions[1]
    assert fun.name == 'support1_function1'
    assert fun.signature == '(a: int, b: float) -> str'
    assert fun.is_coroutine_function

class MockProxy:

    def __init__(self, messages):
        self.messages = messages

    def dispatch(self, func_name: str, *args) -> None:
        self.messages.append((func_name, args))



def test_ast_module_source_to_proxy_no_arguments():
    # language=Python
    target = func_registry.source_to_proxy("""
import js
class Class1:
    def alert(self) -> None:
        js.alert('hello')
    """)
    ast.parse(target)  # verify it's a valid python code

    # exec the generated code
    executed = dict()
    exec(target, executed)
    assert 'Class1' in executed

    messages = []
    c = executed['Class1'](MockProxy(messages))
    c.alert()

    assert messages == [('Class1.alert', ())]


def test_ast_module_source_to_proxy_with_arguments():
    # language=Python
    target = func_registry.source_to_proxy("""
import js
class Class1:
    def alert(self, message:str) -> None:
        js.alert(message)
    """)
    ast.parse(target)  # verify it's a valid python code

    # exec the generated code
    executed = dict()
    exec(target, executed)
    assert 'Class1' in executed

    messages = []

    c = executed['Class1'](MockProxy(messages))
    c.alert('foo')

    assert messages == [('Class1.alert', ('foo',))]
