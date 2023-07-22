from __future__ import annotations

from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Optional, Callable, Dict, AnyStr, Tuple, Any
from urllib.parse import urlparse, parse_qs

from wwwpy.http import HttpRoute, HttpResponse, HttpRequest
from ..webserver import Webserver
from ..webserver import wait_forever


class WsPythonEmbedded(Webserver):
    def __init__(self) -> None:
        super().__init__()
        self.thread: Thread | None = None
        self._routes: Dict[str, HttpRoute] = {}

    def _setup_route(self, route: HttpRoute) -> None:
        self._routes[route.path] = route

    def _start_listen(self) -> None:
        httpd = ThreadingHTTPServer((self.host, self.port), partial(RequestHandler, handler=self._handler))

        def run() -> None:
            print(f'Starting embedded python web server on:\n'
                  f' - http://{self.host}:{self.port}\n'
                  f' - {self.localhost_url()}\n')
            httpd.serve_forever()

        self.thread = Thread(target=run, daemon=True)
        self.thread.start()

    def _handler(self, request: 'RequestHandler') -> bool:
        params, rpath = request.decode_request()
        route = self._routes.get(rpath, None)
        if route is None:
            nf = HTTPStatus.NOT_FOUND
            request.send_bytes(bytes(nf.phrase, 'utf8'), code=nf.value)
        else:
            req = HttpRequest(request.command, request.get_body(), request.get_content_type())
            resp = route.callback(req)
            content = resp.content
            if isinstance(content, str):
                content = bytes(content, 'utf8')
            if not isinstance(content, bytes):
                raise Exception(f'type of the content not supported: {type(content)}')
            request.send_bytes(content, content_type=resp.content_type)
        return True


class RequestHandler(SimpleHTTPRequestHandler):
    query_index = 4
    path_index = 2

    def __init__(self, *args: Any
                 , handler: Callable[['RequestHandler'], bool]
                 , **kwargs: Any) -> None:
        self.handler = handler
        super(RequestHandler, self).__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self.handler(self)

    def do_POST(self) -> None:
        self.handler(self)

    def get_content_type(self) -> str:
        return self.headers.get('Content-Type', '')

    def get_body(self) -> bytes:
        if self.command != 'POST':
            return b''
        content_len = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(content_len)
        return body

    def decode_request(self) -> Tuple[Dict[str, str], str]:
        p = urlparse(self.path)
        query_str = p[self.query_index]
        rpath: str = p[self.path_index]
        di = parse_qs(query_str)
        params = {k: v[0] for k, v in di.items()}
        return params, rpath

    def send_bytes(self, content: bytes, code: int = 200, content_type: str = 'text/plain') -> int:
        self.protocol_version = "HTTP/1.1"
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        return self.wfile.write(content)

    def serve_file(self, directory: str, filename: str) -> None:
        self.directory = directory
        self.path = '/' + filename
        super(RequestHandler, self).do_GET()


if __name__ == '__main__':
    s = WsPythonEmbedded()
    s.set_http_route(HttpRoute('/', lambda req: HttpResponse('ciao', 'text/html')))
    s.start_listen()
    wait_forever()
