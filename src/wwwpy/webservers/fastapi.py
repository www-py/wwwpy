from threading import Thread
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response

from wwwpy.http import HttpRoute, HttpResponse, HttpRequest
from ..webserver import Webserver, wait_forever


class WsFastapi(Webserver):
    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        self.thread: Optional[Thread] = None

    def _setup_route(self, route: HttpRoute):
        async def func(req) -> Response:
            if req.method == 'POST':
                body = await req.body()
                wwwpy_req = HttpRequest(req.method, body, req.headers)
            else:
                wwwpy_req = HttpRequest(req.method, req.body, req.headers)
            return self.to_native_response(route.callback(wwwpy_req))

        self.app.add_route(route.path, route=func, methods=['GET','POST'])

    def to_native_response(self, pn_response: HttpResponse):
        return Response(content=pn_response.content, media_type=pn_response.content_type)

    def _start_listen(self):
        def run():
            uvicorn.run(self.app, host=self.host, port=self.port)

        self.thread = Thread(target=run, daemon=True)
        self.thread.start()


if __name__ == '__main__':
    s = WsFastapi()
    s.set_http_route(HttpRoute('/', lambda req: HttpResponse('ciao', 'text/html')))
    s.start_listen()
    wait_forever()
