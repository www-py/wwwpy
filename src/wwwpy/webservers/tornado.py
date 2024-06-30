from __future__ import annotations

import asyncio
from threading import Thread
from typing import Optional, Awaitable, Union

import tornado.web

import tornado

import threading
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Optional, Callable, Dict, AnyStr, Tuple, Any
from urllib.parse import urlparse, parse_qs

from tornado import gen, websocket
from tornado.httputil import HTTPServerRequest

from wwwpy.http import HttpRoute, HttpResponse, HttpRequest
from wwwpy.http_sansio import SansIOHttpRoute, SansIOHttpRequest, SansIOHttpResponse
from ..webserver import Webserver
from ..webserver import wait_forever
from ..websocket import WebsocketRoute, WebsocketEndpoint


class WsTornado(Webserver):
    def __init__(self):
        super().__init__()
        self.app = tornado.web.Application()
        self.thread: Optional[Thread] = None

    def _setup_route(self, route: HttpRoute | SansIOHttpRoute | WebsocketRoute):
        if isinstance(route, WebsocketRoute):
            self.app.add_handlers(r".*", [(route.path, _WebsocketHandler, dict(route=route))])
        else:
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
        self.route: HttpRoute | SansIOHttpRoute | WebsocketRoute = None
        self._serve = None
        super().__init__(*args, **kwargs)

    def initialize(self, route: HttpRoute | SansIOHttpRoute) -> None:
        self.route = route
        if isinstance(route, SansIOHttpRoute):
            self._serve = self._serve_sansio
        elif isinstance(route, HttpRoute):
            self._serve = self._serve_std
        else:
            raise Exception(f'Unknown route type: {type(route)}')

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Allow-Methods', '*')

    def options(self):
        """/OPTIONS handler for preflight CORS checks."""
        self.set_status(204)
        self.finish()

    async def get(self) -> None:
        await self._serve('GET')

    async def post(self) -> None:
        await self._serve('POST')

    async def _serve_std(self, verb: str):
        body = self.request.body
        response = self.route.callback(HttpRequest(verb, body, self.request.headers.get('Content-Type', '')))
        self.set_header("Content-Type", response.content_type)
        self.write(response.content)

    async def _serve_sansio(self, verb: str):

        request: HTTPServerRequest = self.request
        route = self.route
        sansio_request = SansIOHttpRequest(verb, request.headers.get('Content-Type', ''))
        protocol = route.protocol_factory(sansio_request)
        protocol_terminated = threading.Event()

        async def send_request(data: SansIOHttpResponse | bytes | None):
            if isinstance(data, SansIOHttpResponse):
                self.set_header('Content-Type', data.content_type)
            elif isinstance(data, bytes):
                self.write(data)
                # self.write(data)
            elif data is None:
                await self.flush()
                await self.finish()
                protocol_terminated.set()

                # request.wfile.close()

        # tell the protocol who to call when it wants to send data
        await protocol.on_send(send_request)
        if request.headers.get('Transfer-Encoding', '') == 'chunked':
            raise Exception('chunked not supported')
        else:
            body = self.request.body
            if body:
                protocol.receive(body)
            stream = self.detach()
            try:
                by = await stream.read_bytes(1, True)
                l = len(by)
            except:
                pass
        # while not protocol_terminated.wait(0.5):
        #     pass

        protocol.receive(None)

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        raise_exception(self)


class _WebsocketHandler(websocket.WebSocketHandler):
    route: WebsocketRoute = None
    endpoint: WebsocketEndpoint = None

    def initialize(self, route: WebsocketRoute) -> None:
        self.route = route

    def check_origin(self, origin):
        return True

    def open(self):
        self.endpoint = WebsocketEndpoint(self._on_send)
        self.route.on_connect(self.endpoint)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        self.endpoint.on_message(message)

    def _on_send(self, data: str | bytes | None):
        if data is None:
            self.close()
        else:
            self.write_message(data)

    def on_close(self):
        self.endpoint.on_message(None)


def raise_exception(self: TornadoHandler):
    print("=" * 60)
    print(f'exc! {self.route}')
    raise Exception(self)
