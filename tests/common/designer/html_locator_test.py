import wwwpy.common.designer.html_locator as html_locator
from wwwpy.common.designer.html_locator import Node


def test_locate():
    # language=html
    html = "<div id='foo'><div></div><div id='target'></div></div>"
    path = [Node("div", 0, {'id': 'foo'}), Node("div", 1, {'id': 'target'})]
    actual = html_locator.locate(html, path)
    expect = (25, 48)
    assert actual == expect



def test_serde():
    path = [Node("div", -1, {}), Node("div", 0, {'id': 'foo'}), Node("div", 1, {'id': 'target'})]
    serialized = html_locator.node_path_serialize(path)
    # print on stder
    print(f'\nserialized=={serialized}', )
    deserialized = html_locator.node_path_deserialize(serialized)

    assert path == deserialized, f'\nexpect={path} \ndeserialized={deserialized}'
