from wwwpy.remote.designer.target_path import target_path, Node
from js import document, console


def test_target_path():
    div = document.createElement("div")
    div.innerHTML = """<div id='foo'><div></div><div id="target"></div></div>"""
    target = div.querySelector("#target")
    actual = target_path(target)
    expect = [Node("DIV", -1, {}), Node("DIV", 0, {'id': 'foo'}), Node("DIV", 1, {'id': 'target'})]
    console.log(f'actual={actual}')
    assert actual == expect, f'\nexpect={expect} \nactual={actual}'
