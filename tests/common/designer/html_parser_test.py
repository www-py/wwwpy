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


def test_nested_with_attributes_and_spaces():
    actual = html_to_tree('<div   id="div1" > <p ></p> </div> ')
    children = [CstNode(tag_name='p', position=(19, 27))]
    expect = [CstNode(tag_name='div', position=(0, 34), attributes={'id': 'div1'}, children=children)]
    assert actual == expect


def test_void_tags():
    actual = html_to_tree('<div><input></div>')
    expect = [CstNode(tag_name='div', position=(0, 18), children=[CstNode(tag_name='input', position=(5, 12))])]
    assert actual == expect


def test_void_tags_with_attributes_and_spaces():
    actual = html_to_tree('<div>\n<input id= "input1"  ></div>')
    children = [CstNode(tag_name='input', position=(6, 28), attributes={'id': 'input1'})]
    expect = [CstNode(tag_name='div', position=(0, 34), children=children)]
    assert actual == expect


def test_issue20240727():
    # language=html
    actual = html_to_tree("<div><input/></div><input>")
    expect = [CstNode(tag_name='div', position=(0, 19), children=[CstNode(tag_name='input', position=(5, 13))]),
              CstNode(tag_name='input', position=(19, 26))]
    assert actual == expect
