from pathlib import Path

from wwwpy.common.designer import element_library
from wwwpy.common.tree import print_tree


def test_element_library():
    print('troubleshooting test_element_library')
    ex = Path('/wwwpy_bundle').exists()
    print(f'wwwpy_bundle exists: {ex}')
    if ex:
        print_tree('/wwwpy_bundle')
    el = element_library.element_library()
    assert len(el.elements) > 0
