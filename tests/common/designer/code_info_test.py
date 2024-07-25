from wwwpy.common.designer.code_edit import Attribute, info
from wwwpy.common.designer.code_info import Info, ClassInfo


def test_info():
    target = info(
        """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: HTMLButtonElement = wpc.element()
    """
    )

    expect = Info(classes=[ClassInfo('MyElement', [Attribute('btn1', 'HTMLButtonElement', 'wpc.element()')])])
    assert target == expect


def test_info_with_js_element():
    target = info(
        """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: js.HTMLButtonElement = wpc.element()
    """
    )

    expect = Info(classes=[ClassInfo('MyElement', [Attribute('btn1', 'js.HTMLButtonElement', 'wpc.element()')])])
    assert target == expect
