import sys
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import for_all_webservers
from wwwpy.server import configure
from wwwpy.webserver import Webserver


@pytest.fixture
def restore_sys_path():
    sys_path = sys.path.copy()
    sys_meta_path = sys.meta_path.copy()
    yield
    sys.path = sys_path
    sys.meta_path = sys_meta_path


scenario1 = Path(__file__).parent / 'hot_reload_support' / 'scenario1'


@for_all_webservers()
def test_component1_hot_reload(page: Page, webserver: Webserver, restore_sys_path):
    """In this test we will not use pytester even though we are going to modify the code on the disk
    This could leave the local repo dirty, but it is more convenient than using pytester"""

    remote_init = scenario1 / 'remote' / '__init__.py'
    remote_init.write_text("from js import document;document.body.innerHTML = 'ready'")
    configure.convention(scenario1, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('ready')
    # time.sleep(2)
    # change server side file, should reflect on the client side
    remote_init.write_text("from js import document;document.body.innerHTML = 'modified'")
    expect(page.locator('body')).to_have_text('modified')
