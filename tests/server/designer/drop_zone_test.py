from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import for_all_webservers, restore_sys_path
from wwwpy.server import configure
from wwwpy.webserver import Webserver

drop_zone_support = Path(__file__).parent / "drop_zone_support"


def _setup_remote(tmp_path, remote_init_content):
    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text(remote_init_content)


@for_all_webservers()
def test_drop_zone(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    def runPythonAsync(python: str):
        return page.evaluate(f'pyodide.runPythonAsync(`{python}`)')

    _setup_remote(tmp_path, _test_drop_zone_init)
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator("button#btn1")).to_have_text("ready")

    runPythonAsync("import remote")
    res = runPythonAsync("await remote.start()")
    assert res == ['start-result', 123]

    # the button is 200x100
    # page.mouse.move(50, 25)  # todo, check if the dropzone is highlighted!?
    # page.mouse.click(50, 25)

    expect(page.locator("button#btn1")).to_have_text("begin")


# language=python
_test_drop_zone_init = """from js import document

document.body.innerHTML = '<button id="btn1" style="width: 200px; height: 100px;">ready</button>'
btn1 = document.getElementById('btn1')


async def start():
    btn1.innerHTML = 'begin'
    return ['start-result', 123]
"""
