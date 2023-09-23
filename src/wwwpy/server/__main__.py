import os
from pathlib import Path

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common import iterlib
from wwwpy.resources import library_resources, from_filesystem, from_filepath
from wwwpy.webserver import wait_forever
from wwwpy.webservers.python_embedded import WsPythonEmbedded

if __name__ == '__main__':
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

    resources = iterlib.repeatable_chain(
        library_resources(),
        from_filesystem(working_dir / 'remote', relative_to=working_dir),
        from_filesystem(working_dir / 'common', relative_to=working_dir),
        from_filepath(working_dir / 'common.py', relative_to=working_dir),
        from_filepath(working_dir / 'remote.py', relative_to=working_dir),
    )

    webserver = WsPythonEmbedded()
    bootstrap_python = f'from wwwpy.remote.main import entry_point; await entry_point()'
    webserver.set_http_route(*bootstrap_routes(resources, python=bootstrap_python))
    webserver.set_port(args.port).start_listen()
    wait_forever()
