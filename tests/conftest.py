import json
import threading
from pathlib import Path
from queue import Queue
from threading import Thread

import pytest
from playwright.sync_api import Page, sync_playwright
from xvirt import XVirt

from tests.playwright import playwright_patch_timeout
from wwwpy.bootstrap import bootstrap_routes
from wwwpy.http import HttpRoute, HttpRequest, HttpResponse
from wwwpy.resources import library_resources, from_directory, StringResource
from wwwpy.server import find_port
from wwwpy.webservers.python_embedded import WsPythonEmbedded

_file_parent = Path(__file__).parent


def _setup_page_logger(page: Page):
    page.on('console', lambda msg: print(f'console [{msg.type}] ==== {msg.text}'))
    sep = '\n' + ('=' * 60) + '\n'
    page.on('pageerror', lambda exc: print(f'{sep}uncaught exception through pageerror: {sep}{exc}{sep}'))


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    _setup_page_logger(page)
    yield
    # print("I just experienced that this is not printed if the test fails")


pytest_plugins = ['pytester']

playwright_patch_timeout()

parent_remote = _file_parent / 'remote'


def pytest_xvirt_setup():
    return XVirtImpl()


class XVirtImpl(XVirt):

    def __init__(self):
        self.events = Queue()
        self.close_pw = threading.Event()

    def virtual_path(self) -> str:
        return str(parent_remote)

    def _http_handler(self, req: HttpRequest) -> HttpResponse:
        print(f'server side xvirt_notify_handler({req})')
        self.events.put(req.content)
        return HttpResponse('', 'text/plain')

    def run(self):
        with sync_playwright() as pw: pass  # workaround to run playwright in a new thread. see: https://github.com/microsoft/playwright-python/issues/1685

        webserver = self._start_webserver()

        # start remote with playwright
        def start_playwright():
            from playwright.sync_api import sync_playwright
            p = sync_playwright().start()
            # browser = p.chromium.launch(headless=False)
            browser = p.chromium.launch()
            page = browser.new_page()
            _setup_page_logger(page)
            page.goto(webserver.localhost_url())
            self.close_pw.wait(30)
            # p.stop()

        self._thread = Thread(target=start_playwright, daemon=True)
        self._thread.start()

    def _start_webserver(self):
        xvirt_notify_route = HttpRoute('/xvirt_notify', self._http_handler)
        # read remote conftest content
        remote_conftest = (_file_parent / 'remote_conftest.py').read_text() \
            .replace('#xvirt_notify_path_marker#', '/xvirt_notify')

        resources = [library_resources(),
                     from_directory(parent_remote, relative_to=_file_parent.parent),
                     [
                         # StringResource('tests/__init__.py', ''),
                         # StringResource('pytest.ini', ''),
                         StringResource('conftest.py', remote_conftest),
                         StringResource('remote_test_main.py',
                                        (_file_parent / 'remote_test_main.py').read_text())],

                     ]
        webserver = WsPythonEmbedded()
        invocation_dir, args = self.remote_invocation_params('/wwwpy_bundle')
        invocation_dir_json = json.dumps(invocation_dir)
        args_json = json.dumps(args)
        rootpath = json.dumps('/wwwpy_bundle')
        bootstrap_python = f'import remote_test_main; await remote_test_main.main({rootpath},{invocation_dir_json},{args_json})'
        webserver.set_http_route(*bootstrap_routes(resources, python=bootstrap_python), xvirt_notify_route)
        webserver.set_port(find_port()).start_listen()
        return webserver

    def finalize(self):
        self.close_pw.set()
        # self._thread.join()

    def recv_event(self) -> str:
        return self.events.get(timeout=30)
