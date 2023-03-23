import errno
import socket

_start = 10000
_end = 30000


def find_port() -> int:
    global _start
    while _start < _end:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', _start))
                print(f'findport() -> {_start}')
                return _start
            except socket.error as e:
                if e.errno != errno.EADDRINUSE:
                    raise
                _start += 1
    raise Exception(f'find_port(start={_start},end={_end}) no bindable tcp port found in interval')


if __name__ == '__main__':
    print(find_port())
    print(find_port())
