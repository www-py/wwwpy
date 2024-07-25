from wwwpy.common.designer.html_parser import html_to_tree, CstNode


def test_html_to_tree_empty():
    assert html_to_tree('') == []


def test_html_to_tree():
    actual = html_to_tree('<div></div>')
    expect = [CstNode(tag_name='div', position=(0, 11))]
    assert actual == expect
