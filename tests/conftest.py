import inspect
import os
from types import FunctionType
from typing import Callable, Any

import pytest
from playwright.sync_api import Page, PageAssertions, LocatorAssertions, APIResponseAssertions


@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    page.on('console', lambda msg: print(f'console [{msg.type}] ==== {msg.text}'))
    sep = '\n' + ('=' * 60) + '\n'
    page.on('pageerror', lambda exc: print(f'{sep}uncaught exception through pageerror: {sep}{exc}{sep}'))
    yield
    # print("I just experienced that this is not printed if the test fails")


def patch_playwright_assertions() -> None:
    def env(key: str) -> str:
        v1 = os.environ.get(key, '')
        v2 = os.getenv(key)
        return f'\n{key} v1=`{v1}` v2=`{v2}`'

    string = env('PLAYWRIGHT_PATCH_TIMEOUT') + env('GITHUB_ACTIONS') + env('HOME') + env('PATH')
    raise Exception(f'Env = {string}\nos.environ:\n{os.environ}\n\n')
    timeout_millis = int(os.environ.get('PLAYWRIGHT_PATCH_TIMEOUT', '4000'))
    print(f'Using PLAYWRIGHT_PATCH_TIMEOUT={timeout_millis}')

    # patch playwright assertion timeout to match our configuration
    # this is temporary solution until playwright supports setting custom timeout for assertions
    # github issue: https://github.com/microsoft/playwright-python/issues/1358

    def patch_timeout(_member_obj: FunctionType) -> Callable:
        def patch_timeout_inner(*args, **kwargs) -> Any:
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


patch_playwright_assertions()
