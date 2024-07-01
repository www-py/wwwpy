# wwwpy/pytest_plugin.py
import importlib.util
import inspect
from pathlib import Path

import pytest

from wwwpy.server.pytest.playwright import playwright_setup_page_logger
from wwwpy.server.pytest.xvirt_impl import XVirtImpl


def pytest_addoption(parser):
    parser.addoption("--headful", action="store_true", default=False, help="run tests in headfull mode")


def pytest_configure(config):
    # This function is called before any tests or fixtures are collected.
    # You can add any setup code here.

    # For example, you can add your conftest.py setup code here.
    # Note: You might need to adjust this code to work in this context.
    from wwwpy.server.pytest.playwright import playwright_patch_timeout
    playwright_patch_timeout()


def _get_package_path(package_name: str) -> Path:
    spec = importlib.util.find_spec(package_name)
    if spec:
        package = importlib.import_module(package_name)
        package_path = inspect.getfile(package)
        return Path(package_path)
    return None


@pytest.hookimpl
def pytest_xvirt_setup(config):
    package_name = 'tests.remote'

    location = _get_package_path(package_name)
    folder_remote = location.parent
    folder_root = folder_remote.parent.parent
    headfull = config.getoption("--headful")
    # Now you can use the headfull variable in your setup
    return XVirtImpl(folder_remote, folder_root, headless=not headfull)


def pytest_unconfigure(config):
    # This function is called after all tests and fixtures have been collected.
    # You can add any teardown code here.
    pass


@pytest.fixture(autouse=True)
def before_each_after_each(request):
    if 'page' not in request.node.fixturenames:
        yield
        return
    page = request.getfixturevalue('page')
    playwright_setup_page_logger(page)
    yield
    print("In the hope it is printed. I just experienced that this is not printed if the test fails")
