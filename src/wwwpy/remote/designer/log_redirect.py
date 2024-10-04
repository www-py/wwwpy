import logging
from typing import Callable

from js import console

from wwwpy.remote import set_timeout
from wwwpy.server import rpc


class _CustomHandler(logging.Handler):
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self._emit = callback

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        self._emit(log_entry)


def redirect_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for handler in root.handlers:
        if isinstance(handler, _CustomHandler):
            return

    def emit(msg: str):
        console.log(msg)

        async def _():
            await rpc.server_console_log(msg)

        set_timeout(_)

    formatter = logging.Formatter('%(asctime)s %(levelname).1s %(name)s - %(message)s')
    custom_handler = _CustomHandler(emit)
    custom_handler.setFormatter(formatter)
    root.addHandler(custom_handler)
