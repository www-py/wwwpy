import wwwpy.common.designer.html_locator as html_locator
from wwwpy.common.designer import html_parser
from wwwpy.common.designer.html_locator import Node, NodePath
from wwwpy.common.rpc import serialization


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
    tree = html_parser.html_to_tree(html)
    actual = html_locator.tree_to_path(tree, [1, 2])
    expect = [Node("div", 1, {'id': 'foo'}), Node("button", 2, {'id': 'btn1', 'disabled': None})]
    assert actual == expect

# todo test in development
def todo_test_changing_live_html():
    # language=html
    source = """
<form id="f1">
    <input id="i1" title="title1" required type="text">
    <button id="b1" type="submit">b1-content</button>
    <textarea id="ta1" rows="10" >ta1-content</textarea>
</form>
"""
    # language=html
    live = "<some-insertion></some-insertion>\n" + source
    node_path = serialization.from_json(
        """[{"tag_name": "form", "child_index": 1, "attributes": {"id": "f1"}}, 
        {"tag_name": "button", "child_index": 1, "attributes": {"id": "b1", "type": "submit"}}]""",
        html_locator.NodePath)
    result = html_parser.html_to_tree(live)
    print('ok')
