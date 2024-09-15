from wwwpy.common.designer.code_edit import Attribute
from wwwpy.common.designer.code_info import Info, ClassInfo, Method, info


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


def test_next_attribute_name():
    target = ClassInfo('MyElement', [Attribute('btn1', 'js.HTMLButtonElement', 'wpc.element()')])
    actual = target.next_attribute_name('btn')
    expect = 'btn2'

    assert actual == expect


def test_info_with_method():
    target = info(
        """
import wwwpy.remote.component as wpc
        
class MyElement(wpc.Component):
    def button1__click(self, event):
        pass
""")
    expect = Info(classes=[ClassInfo('MyElement', [], [Method('button1__click', 5, 6)])])
    assert target == expect


def test_info_with_method__multi_line_elements():
    target = info(
        """import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    def button1__click(self,
                       event):
        pass
""")
    expect = Info(classes=[ClassInfo('MyElement', [], [Method('button1__click', 4, 6)])])
    assert target == expect
