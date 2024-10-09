from js import console

from wwwpy.common.designer import log_emit
from wwwpy.remote import set_timeout
from wwwpy.server import rpc


def redirect_logging():
    def emit(msg: str):
        console.log(msg)

        async def _():
            await rpc.server_console_log(msg)

        set_timeout(_)

    log_emit.add_once(emit)
