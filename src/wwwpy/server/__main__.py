from __future__ import annotations

import os
from pathlib import Path

from wwwpy.server import configure
from wwwpy.server.configure import convention


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', default=os.getcwd(),
                        help='Specify alternative directory '
                             '[default:current directory]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()

    working_dir = Path(args.directory).absolute()
    port = args.port

    webserver = configure.start_default(port, working_dir)

    webserver.set_port(port).start_listen()
    webserver.wait_forever()


if __name__ == '__main__':
    main()
