import dataclasses

from wwwpy.common.designer import element_library
from wwwpy.common.designer.element_library import ElementDef
from wwwpy.common.rpc import serialization

import logging

logger = logging.getLogger(__name__)


def test_element_library():
    el = element_library.element_library()
    assert len(el.elements) > 0

def test_hidden_element():
    assert element_library.element_library().by_tag_name('sl-drawer') is None


def test_shown_element():
    assert element_library.element_library().by_tag_name('sl-button') is not None


def test_serialization():
    el = element_library.element_library()

    for e in el.elements:
        e = dataclasses.replace(e)
        e.gen_html = None
        logger.warning(f'serializing {e.tag_name}')
        ser = serialization.to_json(e, ElementDef)
        deser = serialization.from_json(ser, ElementDef)
        assert e == deser
