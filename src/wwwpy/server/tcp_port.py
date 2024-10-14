import errno
import logging
import socket

logger = logging.getLogger(__name__)

_start = (10035 - 1)  # windows doesn't like the previous port range
_end = 30000


def find_port() -> int:
    global _start
    while _start < _end:
        _start += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', _start))
                print(f'findport() -> {_start}')
                return _start
            except socket.error as e:
                if e.errno != errno.EADDRINUSE:
                    raise

    raise Exception(f'find_port(start={_start},end={_end}) no bindable tcp port found in interval')

if __name__ == '__main__':
    print(find_port())
    print(find_port())


def is_port_busy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            if hasattr(socket, "SO_REUSEPORT"):
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            return False
        except socket.error as e:
            # logger.error(f'is_port_busy({port}) -> {e.errno}', exc_info=e)
            if e.errno == errno.EADDRINUSE:
                return True
            raise
