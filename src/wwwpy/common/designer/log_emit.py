import logging
from typing import Callable


class _CustomHandler(logging.Handler):
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self._emit = callback

    def emit(self, record: logging.LogRecord):
        log_entry = self.format(record)
        self._emit(log_entry)


def add_once(emit: Callable[[str], None]):
    for log_name in ['common', 'remote', 'server']:
        logging.getLogger(log_name).setLevel(logging.DEBUG)

    for log_name in ['wwwpy']:
        logging.getLogger(log_name).setLevel(logging.INFO)

    root = logging.getLogger()

    for handler in root.handlers:
        if isinstance(handler, _CustomHandler):
            return

    formatter = logging.Formatter('%(asctime)s %(levelname).1s %(name)s:%(lineno)d - %(message)s')
    custom_handler = _CustomHandler(emit)
    custom_handler.setFormatter(formatter)
    root.addHandler(custom_handler)
