import logging
import os
import sys
from functools import partial
from typing import Iterable

import pytest

from wwwpy.server import find_port
from wwwpy.webserver import Webserver
from wwwpy.webservers.available_webservers import available_webservers

logger = logging.getLogger(__name__)

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


def is_github():
    getenv = os.getenv('GITHUB_ACTIONS')
    print(f'GITHUB_ACTIONS=`{getenv}`')
    return getenv == 'true'


def timeout_multiplier():
    multiplier = 15 if is_github() else 1
    print(f'timeout_multiplier={multiplier}')
    return multiplier
