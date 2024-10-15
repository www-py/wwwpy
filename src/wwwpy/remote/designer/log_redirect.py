from js import console

from wwwpy.common.designer import log_emit
from wwwpy.remote import set_timeout
from wwwpy.server.designer import rpc

_log_buffer = []


async def _process_buffer():
    """This techique avoids the issue of wrong log order"""
    loc = _log_buffer.copy()
    _log_buffer.clear()

    for msg in loc:
        await rpc.server_console_log(msg)


def redirect_logging():
    def emit(msg: str):
        console.log(msg)
        _log_buffer.append(msg)
        set_timeout(_process_buffer)

    log_emit.add_once(emit)
