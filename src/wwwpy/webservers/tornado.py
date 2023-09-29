import asyncio
from threading import Thread
from typing import Optional, Awaitable

import tornado.web

import tornado
from wwwpy import Webserver
from wwwpy.routes import Route


class WsTornado(Webserver):
    def __init__(self):
        super().__init__()
        self.app = tornado.web.Application()
        self.thread: Optional[Thread] = None

    def _setup_route(self, route: Route):
        self.app.add_handlers(r".*", [(route.path, TornadoHandler, dict(route=route))])

    def _start_listen(self):
        async def run_async():
            self.app.listen(self.port, self.host)
            await asyncio.Event().wait()

        def run():
            asyncio.run(run_async())

        self.thread = Thread(target=run, daemon=True)
        self.thread.start()


class TornadoHandler(tornado.web.RequestHandler):

    def __init__(self, *args, **kwargs):
        self.route: Route = None
        super().__init__(*args, **kwargs)

    def initialize(self, route: Route) -> None:
        self.route = route

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', '*')

    def options(self):
        """/OPTIONS handler for preflight CORS checks."""
        self.set_status(204)
        self.finish()

    def get(self) -> None:
        response = self.route.callback()
        self.set_header("Content-Type", response.content_type)
        self.write(response.content)

    def post(self) -> None:
        raise_exception(self)

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        raise_exception(self)


def raise_exception(self: TornadoHandler):
    print("=" * 60)
    print(f'exc! {self.route}')
    raise Exception(self)
