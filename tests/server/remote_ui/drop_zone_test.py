from playwright.sync_api import expect

from tests import for_all_webservers
from tests.server.page_fixture import PageFixture, fixture


@for_all_webservers()
def test_drop_zone(fixture: PageFixture):
    # GIVEN
    page = setup_initial(fixture)

    # THEN
    fixture.assert_evaluate("remote.assert1()")
    fixture.assert_evaluate("remote.assert1_class_before()")

    # WHEN
    page.mouse.move(50, 26)  # the element is the same so no change

    # THEN
    fixture.assert_evaluate("remote.assert1()")
    fixture.evaluate_catch("remote.clear_events()")

    # WHEN
    page.mouse.move(199, 99)

    # THEN
    fixture.assert_evaluate("remote.assert2()")
    fixture.assert_evaluate("remote.assert1_class_after()")

    # WHEN
    page.mouse.move(400, 400)  # it should remove the class

    # THEN
    fixture.assert_evaluate("remote.assert_no_class()")


def setup_initial(fixture):
    # WHEN
    fixture.start_remote(_test_drop_zone_init)
    page = fixture.page

    # THEN
    expect(page.locator("button#btn1")).to_have_text("ready")

    # WHEN
    fixture.evaluate_catch("import remote")
    fixture.evaluate_catch("await remote.start()")
    page.mouse.move(50, 25)  # btn1 is 200x100
    return page


@for_all_webservers()
def test_drop_zone_stop(fixture: PageFixture):
    page = setup_initial(fixture)
    fixture.evaluate_catch("remote.stop()")

    # THEN
    fixture.assert_evaluate("remote.assert_stop()")


# language=python
_test_drop_zone_init = """from js import document, console

from wwwpy.remote.designer.drop_zone import drop_zone_selector, DropZone
from wwwpy.common.designer.html_edit import Position

document.body.innerHTML = '<button id="btn1" style="width: 200px; height: 100px;">ready</button>'
btn1 = document.getElementById('btn1')

drop_zone_events = []


async def start():
    def callback(event: DropZone):
        drop_zone_events.append(event)

    drop_zone_selector.start_selector(callback)


def assert1():
    expected = [DropZone(btn1, Position.beforebegin)]
    success = drop_zone_events == expected
    result = success, f'expected=`{expected}`, actual=`{drop_zone_events}`'
    console.log(f'assert1: {result}')
    return result

def assert1_class_before():
    from wwwpy.remote.designer.drop_zone import _beforebegin_css_class
    expected = _beforebegin_css_class
    success = expected in  btn1.classList
    result = success, f'expected=`{expected}`, actual=`{btn1.classList}`'
    console.log(f'assert1_class_before: {result}')
    return result
    
def assert1_class_after():
    from wwwpy.remote.designer.drop_zone import _afterend_css_class
    expected = _afterend_css_class
    success = expected in btn1.classList
    result = success, f'expected=`{expected}`, actual=`{btn1.classList}`'
    console.log(f'assert1_class_after: {result}')
    return result

def clear_events():
    console.log('clear_events')
    drop_zone_events.clear()

def assert2():
    expected = [DropZone(btn1, Position.afterend)]
    success = drop_zone_events == expected
    result = success, f'expected=`{expected}`, actual=`{drop_zone_events}`'
    console.log(f'assert2: {result}')
    return result

def assert_no_class():
    success = btn1.classList.length == 0
    result = success, f'expected=`no classes`, actual=`{btn1.classList}`'
    console.log(f'assert_no_class: {result}')
    return result

stop_array = []    

def stop():
    stop_array.append(drop_zone_selector.stop())

def assert_stop():
    expected = [DropZone(btn1, Position.beforebegin)]
    success = stop_array == expected
    result = success, f'expected=`{expected}`, actual=`{stop_array}`'
    console.log(f'assert_stop: {result}')
    return result

"""
