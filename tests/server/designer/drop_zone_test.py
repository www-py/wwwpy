from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import for_all_webservers
from wwwpy.bootstrap import wrap_in_tryexcept
from wwwpy.server import configure


def _setup_remote(tmp_path, remote_init_content):
    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text(remote_init_content)


def assertTuple(t):
    __tracebackhide__ = True
    assert t[0], t[1]


class Fixture:
    def __init__(self, page: Page, tmp_path: Path, webserver):
        self.page = page
        self.tmp_path = tmp_path
        self.webserver = webserver

    def evaluate_catch(self, python: str):
        safe_python = wrap_in_tryexcept(python,
                                        'import traceback; from js import console; console.log(f"exception! {traceback.format_exc()}")')
        return self.page.evaluate(f'pyodide.runPythonAsync(`{safe_python}`)')

    def evaluate(self, python: str):
        return self.page.evaluate(f'pyodide.runPythonAsync(`{python}`)')

    def assert_evaluate(self, python: str):
        assertTuple(self.evaluate(python))

    def start_remote(self, _test_drop_zone_init):
        _setup_remote(self.tmp_path, _test_drop_zone_init)
        configure.convention(self.tmp_path, self.webserver)
        self.webserver.start_listen()


@pytest.fixture
def fixture(page: Page, tmp_path, webserver):
    return Fixture(page, tmp_path, webserver)


@for_all_webservers()
def test_drop_zone(fixture: Fixture):
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
    fixture.start_remote(_test_drop_zone_init)
    page = fixture.page
    # WHEN
    page.goto(fixture.webserver.localhost_url())
    # THEN
    expect(page.locator("button#btn1")).to_have_text("ready")
    # WHEN
    fixture.evaluate_catch("import remote")
    fixture.evaluate_catch("await remote.start()")
    page.mouse.move(50, 25)  # btn1 is 200x100
    return page


@for_all_webservers()
def test_drop_zone_stop(fixture: Fixture):
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
