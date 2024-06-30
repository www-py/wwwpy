import json
import threading
from pathlib import Path
from queue import Queue
from threading import Thread

from playwright.sync_api import sync_playwright
from xvirt import XVirt

from wwwpy.server.pytest.playwright import playwright_setup_page_logger, start_playwright, start_playwright_in_thread
from wwwpy.bootstrap import bootstrap_routes
from wwwpy.http import HttpRoute, HttpRequest, HttpResponse
from wwwpy.resources import library_resources, from_directory, StringResource
from wwwpy.server import find_port
from wwwpy.webservers.available_webservers import available_webservers

_file_parent = Path(__file__).parent


class XVirtImpl(XVirt):

    def __init__(self, parent_remote: Path, relative_to: Path, headless: bool = True):
        self.parent_remote = parent_remote
        self.relative_to = relative_to
        self.headless = headless

        self.events = Queue()
        self.close_pw = threading.Event()

    def virtual_path(self) -> str:
        return str(self.parent_remote)

    def _http_handler(self, req: HttpRequest) -> HttpResponse:
        print(f'server side xvirt_notify_handler({req})')
        self.events.put(req.content)
        return HttpResponse('', 'text/plain')

    def run(self):
        webserver = self._start_webserver()
        start_playwright_in_thread(webserver.localhost_url(), self.headless)

    def _start_webserver(self):
        xvirt_notify_route = HttpRoute('/xvirt_notify', self._http_handler)
        # read remote conftest content
        remote_conftest = (_file_parent / 'remote_conftest.py').read_text() \
            .replace('#xvirt_notify_path_marker#', '/xvirt_notify')

        resources = [library_resources(),
                     from_directory(self.parent_remote, relative_to=self.relative_to),
                     [
                         # StringResource('tests/__init__.py', ''),
                         # StringResource('pytest.ini', ''),
                         StringResource('conftest.py', remote_conftest),
                         StringResource('remote_test_main.py',
                                        (_file_parent / 'remote_test_main.py').read_text())],

                     ]
        webserver = available_webservers().new_instance()
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
