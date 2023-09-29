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


@for_all_webservers()
def test_rpc_issue_double_load(page: Page, webserver: Webserver):
    # related to the stubber to being loaded twice
    configure.convention(Path(__file__).parent / 'layer_5_support', webserver)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('42')

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('42')
