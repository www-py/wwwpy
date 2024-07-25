from wwwpy.common.designer.html_edit import html_add, Position
from wwwpy.common.designer.html_locator import Node

# language=html
html = "<div id='foo'><div></div><div id='target'></div></div>"
path = [Node("DIV", 0, {'id': 'foo'}), Node("DIV", 1, {'id': 'target'})]


def test_add_beforebegin():
    actual = html_add(html, 'xyz', path, Position.beforebegin)
    # language=html
    assert actual == "<div id='foo'><div></div>xyz<div id='target'></div></div>"


def test_add_afterend():
    actual = html_add(html, 'xyz', path, Position.afterend)
    # language=html
    assert actual == "<div id='foo'><div></div><div id='target'></div>xyz</div>"
