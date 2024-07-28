from pathlib import Path

from playwright.sync_api import Page, expect

from tests import for_all_webservers
from tests.common import restore_sys_path
from wwwpy.server import configure
from wwwpy.webserver import Webserver

@for_all_webservers()
def test_dev_mode_empty__folder__devmode_create(page: Page, webserver: Webserver, restore_sys_path, tmp_path: Path):
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()
    page.goto(webserver.localhost_url())
    from wwwpy.common import _no_remote_infrastructure_found_text
    expect(page.locator("body")).to_contain_text(_no_remote_infrastructure_found_text)
    (tmp_path / 'remote').mkdir()
    (tmp_path / 'remote' / '__init__.py').write_text('import js; js.document.body.innerHTML = "done"')
    expect(page.locator("body")).to_have_text('done')