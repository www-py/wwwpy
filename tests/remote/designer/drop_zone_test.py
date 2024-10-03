from js import document, MouseEvent
import js
from wwwpy.remote import dict_to_js
from wwwpy.remote.designer import drop_zone


def test__extract_first_with_data_name():
    # GIVEN
    document.body.innerHTML = '<div data-name="bar"><div id="foo"></div></div>'
    foo: js.HTMLDivElement = document.getElementById('foo')
    event = _materialize_mousemove(foo)

    # WHEN
    result = drop_zone._extract_first_with_data_name(event)

    # THEN
    assert result is not None
    assert result == foo.parentElement


def test__the_element_itself_if_has_data_name():
    # GIVEN
    document.body.innerHTML = '<div id="foo" data-name="foo"></div>'
    foo: js.HTMLDivElement = document.getElementById('foo')
    event = _materialize_mousemove(foo)

    # WHEN
    result = drop_zone._extract_first_with_data_name(event)

    # THEN
    assert result is not None
    assert result == foo


def test__if_no_data_name_is_found__return_event_target():
    # GIVEN
    document.body.innerHTML = '<div><div id="foo"></div></div>'
    foo: js.HTMLDivElement = document.getElementById('foo')
    event = _materialize_mousemove(foo)

    # WHEN
    result = drop_zone._extract_first_with_data_name(event)

    # THEN
    assert result is not None
    assert result == foo


def _materialize_mousemove(element):
    mouse_move_event = MouseEvent.new("mousemove", dict_to_js({
        "bubbles": True,
        "cancelable": True,
        "clientX": 150,  # X coordinate of the mouse pointer
        "clientY": 250,  # Y coordinate of the mouse pointer
    }))
    events = []

    def handle_real_event(event: MouseEvent):
        events.append(event)

    element.onmousemove = lambda ev: handle_real_event(ev)
    element.dispatchEvent(mouse_move_event)
    assert len(events) == 1
    event = events[0]
    return event
