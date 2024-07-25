from wwwpy.common.designer.html_parser import html_to_tree, CstNode


def test_html_to_tree_empty():
    assert html_to_tree('') == []


def test_html_to_tree():
    actual = html_to_tree('<div></div>')
    expect = [CstNode(tag_name='div', position=(0, 11))]
    assert actual == expect


def test_nested():
    actual = html_to_tree('<div><p></p></div>')
    expect = [CstNode(tag_name='div', position=(0, 18), children=[CstNode(tag_name='p', position=(5, 12))])]
    assert actual == expect


def test_void_tags():
    actual = html_to_tree('<div><input></div>')
    expect = [CstNode(tag_name='div', position=(0, 18), children=[CstNode(tag_name='input', position=(5, 12))])]
    assert actual == expect
