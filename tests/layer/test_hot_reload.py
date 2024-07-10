from pathlib import Path

from playwright.sync_api import Page, expect

from tests import for_all_webservers, restore_sys_path
from wwwpy.server import configure
from wwwpy.webserver import Webserver


@for_all_webservers()
def test_hot_reload__modified(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    """In this test we will not use pytester even though we are going to modify the code on the disk
    This could leave the local repo dirty, but it is more convenient than using pytester"""

    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text("from js import document;document.body.innerHTML = 'ready'")
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('ready')
    # time.sleep(2)
    # change server side file, should reflect on the client side
    remote_init.write_text("from js import document;document.body.innerHTML = 'modified'")
    expect(page.locator('body')).to_have_text('modified')
