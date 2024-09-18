from wwwpy.common.designer.html_parser import html_to_tree, CstNode, CstAttribute


def test_html_to_tree_empty():
    assert html_to_tree('') == []


def test_html_to_tree():
    actual = html_to_tree('<div></div>')
    expect = [CstNode(tag_name='div', span=(0, 11))]
    assert actual == expect


def test_nested():
    actual = html_to_tree('<div><p></p></div>')
    expect = [CstNode(tag_name='div', span=(0, 18), children=[CstNode(tag_name='p', span=(5, 12))])]
    assert actual == expect


def test_nested_with_attributes_and_spaces():
    actual = html_to_tree('<div   id="div1" > <p ></p> </div> ')
    children = [CstNode(tag_name='p', span=(19, 27))]
    attributes_list = [CstAttribute('id', 'div1', (7, 9), (10, 16))]
    expect = [CstNode(tag_name='div', span=(0, 34), attributes_list=attributes_list, children=children)]
    assert actual == expect


def test_void_tags():
    actual = html_to_tree('<div><input></div>')
    expect = [CstNode(tag_name='div', span=(0, 18), children=[CstNode(tag_name='input', span=(5, 12))])]
    assert actual == expect


def test_void_tags_with_attributes_and_spaces():
    actual = html_to_tree('<div>\n<input id= "input1"  ></div>')  # beware that visually \n takes 2 chars but actually 1
    attributes_list = [CstAttribute('id', 'input1', (13, 15), (17, 25))]
    children = [CstNode(tag_name='input', span=(6, 28), attributes_list=attributes_list)]
    expect = [CstNode(tag_name='div', span=(0, 34), children=children)]
    assert actual == expect


def test_attributes_with_escaped_values():
    actual = html_to_tree('<div id="&lt;div1&gt;"></div>')
    attributes_list = [CstAttribute('id', '<div1>', (5, 7), (8, 22))]
    expect = [CstNode(tag_name='div', span=(0, 29), attributes_list=attributes_list)]
    assert actual == expect


def test_issue20240727():
    # language=html
    actual = html_to_tree("<div><input/></div><input>")
    expect = [CstNode(tag_name='div', span=(0, 19), children=[CstNode(tag_name='input', span=(5, 13))]),
              CstNode(tag_name='input', span=(19, 26))]
    assert actual == expect
