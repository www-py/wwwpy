from wwwpy.common.designer import cst
from wwwpy.common.designer.cst import ClassInfo, AttrInfo, SourceInfo


def test_info():
    target = cst.source_info(
        """
import wwwpy.remote.component as wpc

class MyElement(wpc.Component):
    btn1: HTMLButtonElement = wpc.element()
    """
    )

    expect = SourceInfo(classes=[ClassInfo('MyElement', [AttrInfo('btn1', 'HTMLButtonElement', 'wpc.element()')])])
    assert target == expect
