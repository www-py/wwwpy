import sys
from functools import partial
from types import ModuleType
from typing import Iterable

import pytest

from wwwpy.server import find_port
from wwwpy.webserver import Webserver
from wwwpy.webservers.available_webservers import available_webservers


def _webservers_instances() -> Iterable[Webserver]:
    for i in available_webservers().instances():
        i.set_port(find_port())
        yield i


def for_all_webservers():
    return partial(pytest.mark.parametrize, 'webserver', _webservers_instances(),
                   ids=available_webservers().ids)()


@pytest.fixture
def restore_sys_path():
    sys_path = sys.path.copy()
    sys_meta_path = sys.meta_path.copy()
    yield
    sys.path = sys_path
    sys.meta_path = sys_meta_path
