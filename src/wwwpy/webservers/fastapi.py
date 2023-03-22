from threading import Thread
from typing import Optional

import uvicorn
from fastapi.responses import Response

import wwwpy
from fastapi import FastAPI
from wwwpy import Webserver
from wwwpy.routes import Route


class WsFastapi(Webserver):
    def __init__(self):
        super().__init__()
        self.app = FastAPI()
        self.thread: Optional[Thread] = None

    def _setup_route(self, route: Route):
        def func(*args) -> Response:
            return self.to_native_response(route.callback())

        self.app.add_route(route.path, route=func)

    def to_native_response(self, pn_response: wwwpy.Response):
        return Response(content=pn_response.content, media_type=pn_response.content_type)

    def _start_listen(self):
        def run():
            uvicorn.run(self.app, host=self.host, port=self.port)

        self.thread = Thread(target=run, daemon=True)
        self.thread.start()
