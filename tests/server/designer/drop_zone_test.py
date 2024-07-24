from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import for_all_webservers, restore_sys_path
from wwwpy.bootstrap import wrap_in_tryexcept
from wwwpy.server import configure
from wwwpy.webserver import Webserver


def _setup_remote(tmp_path, remote_init_content):
    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text(remote_init_content)


def assertTuple(t):
    __tracebackhide__ = True
    assert t[0], t[1]


@for_all_webservers()
def test_drop_zone(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    def runPythonAsync(python: str):
        safe_python = wrap_in_tryexcept(python,
                                        'import traceback; from js import console; console.log(f"exception! {traceback.format_exc()}")')
        return page.evaluate(f'pyodide.runPythonAsync(`{safe_python}`)')

    def runPythonAsync2(python: str):
        return page.evaluate(f'pyodide.runPythonAsync(`{python}`)')

    # GIVEN
    _setup_remote(tmp_path, _test_drop_zone_init)
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    # WHEN
    page.goto(webserver.localhost_url())

    # THEN
    expect(page.locator("button#btn1")).to_have_text("ready")

    # WHEN
    runPythonAsync("import remote")
    runPythonAsync("await remote.start()")

    page.mouse.move(50, 25)  # btn1 is 200x100

    # THEN
    assertTuple(runPythonAsync2("remote.assert1()"))
    assertTuple(runPythonAsync2("remote.assert1_class_before()"))

    # WHEN
    page.mouse.move(50, 26)  # the element is the same so no change

    # THEN
    assertTuple(runPythonAsync2("remote.assert1()"))
    runPythonAsync("remote.clear_events()")

    # WHEN
    page.mouse.move(199, 99)

    # THEN
    assertTuple(runPythonAsync2("remote.assert2()"))
    assertTuple(runPythonAsync2("remote.assert1_class_after()"))

    # WHEN
    page.mouse.move(400, 400)  # it should remove the class

    # THEN
    assertTuple(runPythonAsync2("remote.assert_no_class()"))


@for_all_webservers()
def test_drop_zone_stop(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    def runPythonAsync(python: str):
        safe_python = wrap_in_tryexcept(python,
                                        'import traceback; from js import console; console.log(f"exception! {traceback.format_exc()}")')
        return page.evaluate(f'pyodide.runPythonAsync(`{safe_python}`)')

    def runPythonAsync2(python: str):
        return page.evaluate(f'pyodide.runPythonAsync(`{python}`)')

    # GIVEN
    _setup_remote(tmp_path, _test_drop_zone_init)
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    # WHEN
    page.goto(webserver.localhost_url())

    # THEN
    expect(page.locator("button#btn1")).to_have_text("ready")

    # WHEN
    runPythonAsync("import remote")
    runPythonAsync("await remote.start()")

    page.mouse.move(50, 25)  # btn1 is 200x100
    runPythonAsync("await remote.stop()")

    # THEN
    assertTuple(runPythonAsync2("remote.assert_stop()"))

# language=python
_test_drop_zone_init = """from js import document, console

from wwwpy.remote.designer.drop_zone import drop_zone_selector, DropZone, Position

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
    
def stop():
    drop_zone_selector.stop()

"""
