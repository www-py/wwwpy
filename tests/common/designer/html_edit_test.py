from wwwpy.common.designer.html_edit import html_add, Position, html_edit, html_attribute_set
from wwwpy.common.designer.html_locator import Node

# language=html
html = "<div id='foo'><div></div><div id='target'></div></div>"
path = [Node("div", 0, {'id': 'foo'}), Node("div", 1, {'id': 'target'})]


def test_add_beforebegin():
    actual = html_add(html, 'xyz', path, Position.beforebegin)
    # language=html
    assert actual == "<div id='foo'><div></div>xyz<div id='target'></div></div>"


def test_add_afterend():
    actual = html_add(html, 'xyz', path, Position.afterend)
    # language=html
    assert actual == "<div id='foo'><div></div><div id='target'></div>xyz</div>"


def test_edit():
    actual = html_edit(html, 'xyz', path)
    # language=html
    assert actual == "<div id='foo'><div></div>xyz</div>"


class TestAttributeSet:
    def test_attribute_set(self):
        actual = html_attribute_set(html, path, 'id', 'bar')
        # language=html
        assert actual == "<div id='foo'><div></div><div id='bar'></div></div>"

    def test_attribute_set_should_not_change_quote_char(self):
        # language=html
        html = """<div id="foo"><div></div><div id="target"></div></div>"""
        path = [Node("div", 0, {'id': 'foo'}), Node("div", 1, {'id': 'target'})]

        actual = html_attribute_set(html, path, 'id', 'bar')
        # language=html
        assert actual == """<div id="foo"><div></div><div id="bar"></div></div>"""
