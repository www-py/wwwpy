from __future__ import annotations

import os
from pathlib import Path

from wwwpy.server import configure
from wwwpy.webserver import wait_forever


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
    parser.add_argument('dev', action='store', default=False, type=bool, help="Run in development mode")
    args = parser.parse_args()

    working_dir = Path(args.directory).absolute()
    configure.start_default(args.port, working_dir, dev_mode=args.dev)

    import webbrowser
    webbrowser.open(f'http://localhost:{args.port}')
    wait_forever()


if __name__ == '__main__':
    main()
