from pathlib import Path

from playwright.sync_api import Page, expect

from tests import for_all_webservers
from wwwpy.resources import from_directory
from wwwpy.server import configure
from wwwpy.webserver import Webserver

file_parent = Path(__file__).parent


@for_all_webservers()
def test_server_convention_a(page: Page, webserver: Webserver):
    _test_convention('convention_a', page, webserver)


@for_all_webservers()
def test_server_convention_b(page: Page, webserver: Webserver):
    _test_convention('convention_b', page, webserver)


@for_all_webservers()
def test_server_convention_c_async(page: Page, webserver: Webserver):
    _test_convention('convention_c_async', page, webserver)


@for_all_webservers()
def test_server_convention_c_sync(page: Page, webserver: Webserver):
    _test_convention('convention_c_sync', page, webserver)


def _test_convention(directory, page, webserver):
    configure._convention(file_parent / 'layer_4_support' / directory, webserver)
    webserver.start_listen()
    page.goto(webserver.localhost_url())
    expect(page.locator('id=tag1')).to_have_value(directory)


@for_all_webservers()
def test_configure_add_to_remote(page: Page, webserver: Webserver):
    additional = file_parent / 'layer_4_support' / 'additional'
    configure._conventional_resources_additional_append(
        from_directory(additional / 'addon_module', relative_to=additional))

    configure._convention(additional, webserver)
    webserver.start_listen()
    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('additional')
