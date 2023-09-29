from __future__ import annotations

from pathlib import Path

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common import iterlib
from wwwpy.resources import library_resources, from_filesystem, from_filepath
from wwwpy.webserver import Webserver, wait_forever
from wwwpy.webservers.available_webservers import available_webservers


def start_default(port: int, working_dir: Path):
    webserver = available_webservers().new_instance()

    convention(working_dir, webserver)

    webserver.set_port(port).start_listen()
    wait_forever()


def convention(working_dir, webserver):
    """
    Convention for a wwwpy server.
    It configures the webserver to serve the files from the working directory.
    It also configures the webserver to serve the files from the library.
    """
    resources = iterlib.repeatable_chain(
        library_resources(),
        from_filesystem(working_dir / 'remote', relative_to=working_dir),
        from_filesystem(working_dir / 'common', relative_to=working_dir),
        from_filepath(working_dir / 'common.py', relative_to=working_dir),
        from_filepath(working_dir / 'remote.py', relative_to=working_dir),
    )
    bootstrap_python = f'from wwwpy.remote.main import entry_point; await entry_point()'
    webserver.set_http_route(*bootstrap_routes(resources, python=bootstrap_python))

    return webserver
