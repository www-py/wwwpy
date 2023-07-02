import inspect
import os
from pathlib import Path
from queue import Queue
from types import FunctionType
from typing import Callable, Any

import pytest
from playwright.sync_api import Page, PageAssertions, LocatorAssertions, APIResponseAssertions
from py._path.local import LocalPath
from xvirt.events import EvtCollectionFinish, Evt, EvtRuntestLogreport

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common import iterlib
from wwwpy.http import HttpRoute, HttpRequest, HttpResponse
from wwwpy.resources import library_resources, from_filesystem, StringResource
from wwwpy.server import find_port
from wwwpy.webservers.python_embedded import WsPythonEmbedded

parent = Path(__file__).parent


def _setup_page_logger(page: Page):
    page.on('console', lambda msg: print(f'console [{msg.type}] ==== {msg.text}'))
    sep = '\n' + ('=' * 60) + '\n'
    page.on('pageerror', lambda exc: print(f'{sep}uncaught exception through pageerror: {sep}{exc}{sep}'))


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    _setup_page_logger(page)
    yield
    # print("I just experienced that this is not printed if the test fails")


def patch_playwright_assertions() -> None:
    def PLAYWRIGHT_PATCH_TIMEOUT_MILLIS() -> int:
        return int(os.environ.get('PLAYWRIGHT_PATCH_TIMEOUT_MILLIS', '4000'))

    print(f'Using PLAYWRIGHT_PATCH_TIMEOUT, current value={PLAYWRIGHT_PATCH_TIMEOUT_MILLIS()}')

    # patch playwright assertion timeout to match our configuration
    # this is temporary solution until playwright supports setting custom timeout for assertions
    # github issue: https://github.com/microsoft/playwright-python/issues/1358

    def patch_timeout(_member_obj: FunctionType) -> Callable:
        def patch_timeout_inner(*args, **kwargs) -> Any:
            timeout_millis = PLAYWRIGHT_PATCH_TIMEOUT_MILLIS()
            parameters = inspect.signature(_member_obj).parameters
            timeout_arg_index = list(parameters.keys()).index("timeout")
            if timeout_arg_index >= 0:
                if len(args) > timeout_arg_index:
                    args = list(args)  # type: ignore
                    args[timeout_arg_index] = timeout_millis  # type: ignore
                elif 'timeout' not in kwargs:
                    kwargs["timeout"] = timeout_millis
            return _member_obj(*args, **kwargs)

        return patch_timeout_inner

    for assertion_cls in [PageAssertions, LocatorAssertions, APIResponseAssertions]:
        for member_name, member_obj in inspect.getmembers(assertion_cls):
            if isinstance(member_obj, FunctionType):
                if "timeout" in inspect.signature(member_obj).parameters:
                    setattr(assertion_cls, member_name, patch_timeout(member_obj))


pytest_plugins = ['pytester']

patch_playwright_assertions()


def load_dotenv(env: Path):
    if not env.exists():
        return

    for line in env.read_text().splitlines():
        line = line.strip()
        if line.startswith('#') or line == '':
            continue
        parts = line.split('=', 1)
        if len(parts) == 2:
            key, value = tuple(map(lambda s: s.strip(), parts))
            print(f'.env loading `{key}={value}`')
            os.environ[key] = value


def pytest_sessionstart(session: pytest.Session):
    load_dotenv(session.config.rootpath / '.env')

    pluginmanager = session.config.pluginmanager
    # _playwright = pluginmanager.get_plugin('playwright')
    # pluginmanager.unregister(name='playwright') # weird it does not change th
    pass


parent_remote = str(parent / 'remote')


def pytest_xvirt_setup(config, xvirt_packages):
    xvirt_packages.append(parent_remote)


parent2 = parent

pytest_xvirt_abs = Path('/home/simone/Documents/python/pytest-xvirt/src/xvirt')


def pytest_xvirt_collect_file(file_path, path, parent, events_handler):
    # queue to receive json events from remote
    events = Queue()

    def get_next_event():
        return Evt.from_json(events.get(timeout=10))

    # define route to receive events from remote
    def xvirt_notify_handler(req: HttpRequest) -> HttpResponse:
        print('server side xvirt_notify_handler')
        events.put(req.content)
        return HttpResponse('', 'text/plain')

    xvirt_notify_route = HttpRoute('/xvirt_notify', xvirt_notify_handler)

    # start webserver
    # read remote conftest content
    remote_conftest = (parent2 / 'remote_conftest.py').read_text().replace('#xvirt_notify_path_marker#',
                                                                           '/xvirt_notify')

    resources = iterlib.repeatable_chain(library_resources(),
                                         from_filesystem(parent2 / 'remote', relative_to=parent2.parent),
                                         [StringResource('conftest.py', remote_conftest),
                                          StringResource('remote_test_main.py',
                                                         (parent2 / 'remote_test_main.py').read_text()),
                                          ],
                                         )
    webserver = WsPythonEmbedded()
    webserver.set_http_route(
        *bootstrap_routes(resources, python='import remote_test_main; await remote_test_main.main()'),
        xvirt_notify_route)
    webserver.set_port(find_port()).start_listen()

    # start remote with playwright
    from playwright.sync_api import sync_playwright

    # with sync_playwright() as p:
    p = sync_playwright().__enter__()
    # browser = p.chromium.launch(headless=False)
    browser = p.chromium.launch()
    page = browser.new_page()
    _setup_page_logger(page)
    page.goto(webserver.localhost_url())
    # magic start
    # page.wait_for_selector('text=All tests passed')
    return events_handler(get_next_event)
    evt_cf = get_next_event()
    # magic end
    assert isinstance(evt_cf, EvtCollectionFinish)
    from xvirt.collectors import VirtCollector
    result = VirtCollector.from_parent(parent, name=file_path.name)
    result.nodeid_array = evt_cf.node_ids

    # report phase
    config = parent.config
    recv_count = 0
    while recv_count < len(evt_cf.node_ids):
        evt_rep = get_next_event()
        assert isinstance(evt_rep, EvtRuntestLogreport)
        rep = config.hook.pytest_report_from_serializable(config=config, data=evt_rep.data)
        config.hook.pytest_runtest_logreport(report=rep)
        recv_count += 1

    # page.close()
    # browser.close()
    return result

# TODO eseguendo il test su tests dice 'no tests were found'
# pero se si esegue su `remote` funziona
