import wwwpy.common.designer.html_locator as html_locator
from wwwpy.common.designer.html_locator import Node


def test_locate():
    html_locator.locate('<div></div>', [])


def test_serde():
    path = [Node("DIV", -1, {}), Node("DIV", 0, {'id': 'foo'}), Node("DIV", 1, {'id': 'target'})]
    serialized = html_locator.node_path_serialize(path)
    # print on stder
    print(f'\nserialized=={serialized}', )
    deserialized = html_locator.node_path_deserialize(serialized)

    assert path == deserialized, f'\nexpect={path} \ndeserialized={deserialized}'
