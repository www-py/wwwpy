import sys
from pathlib import Path

import pytest
from playwright.sync_api import Page

from wwwpy.bootstrap import wrap_in_tryexcept
from wwwpy.common import reloader
from wwwpy.server import configure


class PageFixture:
    def __init__(self, page: Page, tmp_path: Path, webserver):
        self.page = page
        self.tmp_path = tmp_path
        self.webserver = webserver
        self.remote = self.tmp_path / 'remote'
        self.remote_init = self.remote / '__init__.py'
        self.dev_mode = False

    def set_path(self, path):
        self.tmp_path = path
        self.remote = self.tmp_path / 'remote'
        self.remote_init = self.remote / '__init__.py'

    def evaluate_catch(self, python: str):
        safe_python = wrap_in_tryexcept(python,
                                        'import traceback; from js import console; console.log(f"exception! {traceback.format_exc()}")')
        return self.page.evaluate(f'pyodide.runPythonAsync(`{safe_python}`)')

    def evaluate(self, python: str):
        return self.page.evaluate(f'pyodide.runPythonAsync(`{python}`)')

    def assert_evaluate(self, python: str):
        __tracebackhide__ = True
        t = self.evaluate(python)
        assert t[0], t[1]

    def start_remote(self, remote_init_content: str = None):
        remote_init = self.remote_init
        remote_init.parent.mkdir(parents=True, exist_ok=True)
        if remote_init_content:
            remote_init.write_text(remote_init_content)
        configure.convention(self.tmp_path, self.webserver, dev_mode=self.dev_mode)
        self.webserver.start_listen()
        self.page.goto(self.webserver.localhost_url())

    def write_module(self, module_path: str, content: str):
        file = self.tmp_path / module_path
        parent = file.parent
        parent.mkdir(parents=True, exist_ok=True)
        file.write_text(content)
        init = parent / '__init__.py'
        if not init.exists():
            init.touch()

    def unload(self):
        reloader.unload_path(str(self.tmp_path))


@pytest.fixture
def fixture(page: Page, tmp_path, webserver):
    sys_path = sys.path.copy()
    sys_meta_path = sys.meta_path.copy()
    fix = PageFixture(page, tmp_path, webserver)
    try:
        yield fix
    finally:
        sys.path = sys_path
        sys.meta_path = sys_meta_path
        fix.unload()
