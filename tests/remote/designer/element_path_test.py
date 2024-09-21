import sys

from js import document

from tests.common import dyn_sys_path
from wwwpy.common.designer.html_locator import Node
from wwwpy.remote.designer.element_path import element_path, element_to_node_path


def test_target_path_to_component(tmp_path, dyn_sys_path):
    # GIVEN
    dyn_sys_path.write_module('', 'component1.py', '''import js

import wwwpy.remote.component as wpc


class Component1(wpc.Component):
    btn1: js.HTMLButtonElement = wpc.element()

    def connectedCallback(self):
        self.element.innerHTML = """
        <div></div>
        <div class='class1'>foo
            <button data-name='btn1' id='btn1id'>bar</button>
        </div>
    """
    ''')

    from component1 import Component1
    component1 = Component1()

    document.body.innerHTML = ''
    document.body.appendChild(component1.element)

    target = document.querySelector("#btn1id")
    assert target

    # WHEN
    actual = element_path(target)

    # THEN
    path = [Node("div", 1, {'class': 'class1'}),
            Node("button", 0, {'data-name': 'btn1', 'id': 'btn1id'})]

    assert actual.class_module == 'component1'
    assert actual.class_name == 'Component1'
    assert actual.path == path


def test_target_path__without_component():
    # GIVEN

    document.body.innerHTML = """
        <div></div>
        <div class='class1'>foo
            <button data-name='btn1' id='btn1id'>bar</button>
        </div>
    """

    target = document.querySelector("#btn1id")
    assert target

    # WHEN
    actual = element_path(target)

    # THEN
    assert actual is None


def test_target_path__unattached_piece_of_dom():
    # GIVEN
    document.body.innerHTML = ''
    div = document.createElement("div")
    div.setAttribute('attr1', 'foo')
    div.innerHTML = """
        <div></div>
        <div class='class1'>foo
            <button data-name='btn1' id='btn1id'>bar</button>
        </div>
    """

    target = div.querySelector("#btn1id")
    assert target

    # WHEN
    actual = element_path(target)

    # THEN
    assert actual is None


def test_element_to_node_path():
    # GIVEN
    document.body.innerHTML = """
        <div></div>
        <div class='class1'>foo
            <button data-name='btn1' id='btn1id'>bar</button>
        </div>
    """

    target = document.querySelector("#btn1id")
    assert target

    # WHEN
    actual = element_to_node_path(target)

    # THEN
    path = [Node("div", 1, {'class': 'class1'}),
            Node("button", 0, {'data-name': 'btn1', 'id': 'btn1id'})]

    assert actual == path
