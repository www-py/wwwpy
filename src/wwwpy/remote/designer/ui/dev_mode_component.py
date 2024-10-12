import wwwpy.remote.component as wpc
import js
from wwwpy.remote import dict_to_js
from pyodide.ffi import create_proxy


class DevModeComponent(wpc.Component, tag_name='wwwpy-dev-mode'):
    pass


def show():
    from . import toolbox  # noqa
    js.document.body.insertAdjacentHTML('beforeend', '<wwwpy-toolbox></wwwpy-toolbox>')
