from wwwpy.common.designer.html_edit import html_add, Position
from wwwpy.common.designer.html_locator import Node


def test_add_beforebegin():
    # language=html
    html = "<div id='foo'><div></div><div id='target'></div></div>"
    path = [Node("DIV", 0, {'id': 'foo'}), Node("DIV", 1, {'id': 'target'})]

    actual = html_add(html, 'xyz', path, Position.beforebegin)
    # language=html
    expect = "<div id='foo'><div></div>xyz<div id='target'></div></div>"

    assert actual == expect

def test_add_afterend():
    # language=html
    html = "<div id='foo'><div></div><div id='target'></div></div>"
    path = [Node("DIV", 0, {'id': 'foo'}), Node("DIV", 1, {'id': 'target'})]

    actual = html_add(html, 'xyz', path, Position.afterend)
    # language=html
    expect = "<div id='foo'><div></div><div id='target'></div>xyz</div>"

    assert actual == expect
