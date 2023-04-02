import inspect
import os
from pathlib import Path
from types import FunctionType
from typing import Callable, Any

import pytest
from playwright.sync_api import Page, PageAssertions, LocatorAssertions, APIResponseAssertions
from py._path.local import LocalPath


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    page.on('console', lambda msg: print(f'console [{msg.type}] ==== {msg.text}'))
    sep = '\n' + ('=' * 60) + '\n'
    page.on('pageerror', lambda exc: print(f'{sep}uncaught exception through pageerror: {sep}{exc}{sep}'))
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


# -- pytest remote tests
def pytest_collect_file(file_path: Path, path: LocalPath, parent):
    # if self_file == file_path:
    #     return StbtCollector.from_parent(parent, path=file_path.parent)
    # else:
    #     None
    # parents = list(file_path.parents)
    # if path.ext == ".py" and accepted_root in parents:
    #     return StbtCollector.from_parent(parent, path=file_path)
    # else:
    return None
