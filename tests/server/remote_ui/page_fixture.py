from pathlib import Path

from playwright.sync_api import Page

from wwwpy.bootstrap import wrap_in_tryexcept
from wwwpy.server import configure


class Fixture:
    def __init__(self, page: Page, tmp_path: Path, webserver):
        self.page = page
        self.tmp_path = tmp_path
        self.webserver = webserver

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

    def start_remote(self, _test_drop_zone_init):
        remote_init = self.tmp_path / 'remote' / '__init__.py'
        remote_init.parent.mkdir(parents=True)
        remote_init.write_text(_test_drop_zone_init)
        configure.convention(self.tmp_path, self.webserver)
        self.webserver.start_listen()
        self.page.goto(self.webserver.localhost_url())
