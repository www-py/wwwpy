from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import for_all_webservers, restore_sys_path
from wwwpy.server import configure
from wwwpy.webserver import Webserver

drop_zone_support = Path(__file__).parent / "drop_zone_support"


@for_all_webservers()
def test_drop_zone(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text(  # language=python
        """
from js import document
document.body.innerHTML = '<button id="btn1" style="width: 200px; height: 100px;">unchanged</button>'

"""
    )
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator("button#btn1")).to_have_text("unchanged")
