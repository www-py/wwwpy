from pathlib import Path

from playwright.sync_api import Page, expect

from tests import for_all_webservers
from wwwpy.server import configure
from wwwpy.webserver import Webserver


@for_all_webservers()
def test_rpc(page: Page, webserver: Webserver):
    configure.convention(Path(__file__).parent / 'layer_5_support', webserver)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('42')
