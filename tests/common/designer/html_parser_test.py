from wwwpy.common.designer.html_parser import html_to_tree, CstNode, CstAttribute, CstNodeList


def test_html_to_tree_empty():
    assert html_to_tree('') == []


def test_html_to_tree():
    actual = html_to_tree('<div></div>')
    expect = [CstNode(tag_name='div', span=(0, 11), attr_span=(4, 4))]
    assert actual == expect


def test_nested():
    actual = html_to_tree('<div><p></p></div>')
    p_node = CstNode(tag_name='p', span=(5, 12), attr_span=(7, 7))
    expect = [CstNode(tag_name='div', span=(0, 18), attr_span=(4, 4), children=CstNodeList([p_node]))]
    assert actual == expect

    actual_div = actual[0]
    actual_p = actual_div.children[0]
    assert actual_div.parent is None
    assert actual_div.level == 0
    assert actual_p.parent == actual_div
    assert actual_p.level == 1


def test_nested_with_attributes_and_spaces():
    actual = html_to_tree('<div   id="div1" > <p ></p> </div> ')
    children = CstNodeList([CstNode(tag_name='p', span=(19, 27), attr_span=(21, 22))])
    attributes_list = [CstAttribute('id', 'div1', (7, 9), (10, 16))]
    expect = [CstNode(tag_name='div', span=(0, 34), attr_span=(4, 17)
                      , attributes_list=attributes_list, children=children)]
    assert actual == expect


def test_attribute_without_value():
    actual = html_to_tree('<div foo></div>')
    attributes_list = [CstAttribute('foo', None, (5, 8), None)]
    expect = [CstNode(tag_name='div', span=(0, 15), attr_span=(4, 8), attributes_list=attributes_list)]
    assert actual == expect


def test_void_tags():
    actual = html_to_tree('<div><input></div>')
    expect = [CstNode(tag_name='div', span=(0, 18), attr_span=(4, 4),
                      children=CstNodeList([CstNode(tag_name='input', span=(5, 12), attr_span=(11, 11))]))]
    assert actual == expect


def test_void_tags_with_attributes_and_spaces():
    actual = html_to_tree('<div>\n<input id= "input1"  ></div>')  # beware that visually \n takes 2 chars but actually 1
    attributes_list = [CstAttribute('id', 'input1', (13, 15), (17, 25))]
    children = [CstNode(tag_name='input', span=(6, 28), attr_span=(12, 12 + 15), attributes_list=attributes_list)]
    expect = [CstNode(tag_name='div', span=(0, 34), attr_span=(4, 4), children=CstNodeList(children))]
    assert actual == expect


def test_attributes_with_escaped_values():
    actual = html_to_tree('<div id="&lt;div1&gt;"></div>')
    attributes_list = [CstAttribute('id', '<div1>', (5, 7), (8, 22))]
    expect = [CstNode(tag_name='div', span=(0, 29), attr_span=(4, 22), attributes_list=attributes_list)]
    assert actual == expect


def test_issue20240727():
    # language=html
    actual = html_to_tree("<div><input/></div><input>")
    expect = [CstNode(tag_name='div', span=(0, 19), attr_span=(4, 4),
                      children=CstNodeList([CstNode(tag_name='input', span=(5, 13), attr_span=(11, 11))])),
              CstNode(tag_name='input', span=(19, 26), attr_span=(25, 25))]
    assert actual == expect


def test_attribute_span_for_autoclosing():
    # language=html
    actual = html_to_tree("<input/>")
    assert actual == [CstNode(tag_name='input', span=(0, 8), attr_span=(6, 6))]
