import wwwpy.common.designer.html_locator as html_locator
from wwwpy.common.designer.html_locator import Node


def test_locate():
    # language=html
    html = "<div id='foo'><div></div><div id='target'></div></div>"
    path = [Node("div", 0, {'id': 'foo'}), Node("div", 1, {'id': 'target'})]
    actual = html_locator.locate_span(html, path)
    expect = (25, 48)
    assert actual == expect


def test_serde():
    path = [Node("div", -1, {}), Node("div", 0, {'id': 'foo'}), Node("div", 1, {'id': 'target'})]
    serialized = html_locator.node_path_serialize(path)
    # print on stder
    print(f'\nserialized=={serialized}', )
    deserialized = html_locator.node_path_deserialize(serialized)

    assert path == deserialized, f'\nexpect={path} \ndeserialized={deserialized}'


def test_cst_node_to_node():
    # language=html
    html = "<b></b><div id='foo'><input><br><button id='btn1' disabled></button></div>"
    tree = html_locator.html_to_tree(html)
    actual = html_locator.tree_to_path(tree, [1, 2])
    expect = [Node("div", 1, {'id': 'foo'}), Node("button", 2, {'id': 'btn1', 'disabled': None})]
    assert actual == expect
