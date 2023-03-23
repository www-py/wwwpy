from functools import partial
from types import ModuleType

import pytest


from wwwpy.server import find_port
from wwwpy.webservers.available_webservers import available_webservers


def for_all_webservers():
    return partial(pytest.mark.parametrize, 'webserver', available_webservers().instances(),
                   ids=available_webservers().ids)()
