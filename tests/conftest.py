from pathlib import Path

import pytest
from playwright.sync_api import Page

from wwwpy.server.pytest.playwright import playwright_patch_timeout, playwright_setup_page_logger
from tests.xvirt_impl import XVirtImpl

_file_parent = Path(__file__).parent


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    playwright_setup_page_logger(page)
    yield
    # print("I just experienced that this is not printed if the test fails")


pytest_plugins = ['pytester']

playwright_patch_timeout()

parent_remote = _file_parent / 'remote'


def pytest_xvirt_setup():
    return XVirtImpl(parent_remote, _file_parent.parent)
