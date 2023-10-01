from pathlib import Path
from time import sleep

from wwwpy.bootstrap import bootstrap_routes
from wwwpy.common import iterlib
from wwwpy.resources import library_resources, from_directory
from wwwpy.webservers.python_embedded import WsPythonEmbedded

parent = Path(__file__).parent


def quickstart():
    resources = iterlib.repeatable_chain(library_resources(), from_directory(parent, relative_to=parent.parent))
    webserver = WsPythonEmbedded()
    webserver.set_http_route(*bootstrap_routes(resources, python='import play.remote; await play.remote.main()'))
    webserver.start_listen()
    while True: sleep(10)


if __name__ == '__main__':
    quickstart()
