from __future__ import annotations

import threading
from http import HTTPStatus
from time import sleep
from typing import Callable

from tests import for_all_webservers
from wwwpy.http import HttpRoute, HttpResponse, HttpRequest
from wwwpy.http_sansio import SansIOHttpProtocol, SansIOHttpRequest, SansIOHttpResponse, SansIOHttpRoute
from wwwpy.server import find_port
from wwwpy.server.fetch import sync_fetch_response
from wwwpy.webserver import Webserver


class TestHttpRoute:

    @for_all_webservers()
    def test_webservers_get(self, webserver: Webserver):
        response_a = HttpResponse('a', 'text/plain')
        response_b = HttpResponse('b', 'text/html')

        webserver.set_http_route(HttpRoute('/b', lambda req: response_b))
        webserver.set_http_route(HttpRoute('/', lambda req: response_a))

        webserver.set_port(find_port()).start_listen()

        url = webserver.localhost_url()

        assert sync_fetch_response(url) == response_a
        assert sync_fetch_response(url + '/b') == response_b

    @for_all_webservers()
    def test_webservers_post(self, webserver: Webserver):
        # GIVEN
        response_a = HttpResponse('a', 'text/plain')
        actual_request: HttpRequest | None = None

        def handler(req: HttpRequest) -> HttpResponse:
            nonlocal actual_request
            actual_request = req
            return response_a

        http_route = HttpRoute('/route1', handler)

        webserver.set_http_route(http_route).start_listen()

        url = webserver.localhost_url()

        # WHEN
        actual_response = sync_fetch_response(url + '/route1', method='POST', data='post-body')

        # THEN
        assert actual_response == response_a
        assert actual_request.method == 'POST'
        assert actual_request.content.decode('utf8') == 'post-body'


class TestSansIOHttpRoute:

    @for_all_webservers()
    def test_webservers_get(self, webserver: Webserver):
        requests = []

        class SimpleProtocol(SansIOHttpProtocol):
            send = None

            def __init__(self, request: SansIOHttpRequest, response: str, content_type: str):
                self.response = response
                self.content_type = content_type
                requests.append(request)

            def on_send(self, send: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
                send(SansIOHttpResponse(self.content_type))
                send(self.response.encode('utf8'))
                send(None)

            def receive(self, data: bytes | None) -> None:
                raise Exception('This should not be called, it is a GET request, so no bytes should be received.')

        webserver.set_http_route(SansIOHttpRoute('/b', lambda req: SimpleProtocol(req, 'b', 'text/html')))
        webserver.set_http_route(SansIOHttpRoute('/', lambda req: SimpleProtocol(req, 'a', 'text/plain')))

        webserver.set_port(find_port()).start_listen()

        url = webserver.localhost_url()

        assert sync_fetch_response(url) == HttpResponse('a', 'text/plain')
        assert sync_fetch_response(url + '/b') == HttpResponse('b', 'text/html')
        assert len(requests) == 2

    @for_all_webservers()
    def test_webservers_post(self, webserver: Webserver):
        # GIVEN

        class SimpleProtocol(SansIOHttpProtocol):
            received = None

            def on_send(self, send: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
                send(SansIOHttpResponse('text/plain'))
                send(b'hello')
                send(None)
                self.received = []

            def receive(self, data: bytes | None) -> None:
                self.received.append(data)

        protocol = SimpleProtocol()

        webserver.set_http_route(SansIOHttpRoute('/route1', lambda req: protocol)).start_listen()

        url = webserver.localhost_url()

        # WHEN
        actual_response = sync_fetch_response(url + '/route1', method='POST', data='post-body')

        # THEN
        assert actual_response == HttpResponse('hello', 'text/plain')
        assert protocol.received == [b'post-body', None]

    @for_all_webservers()
    def test_webservers_post__response_delayed(self, webserver: Webserver):
        # GIVEN

        class SimpleProtocol(SansIOHttpProtocol):
            received = None

            def on_send(self, send: Callable[[SansIOHttpResponse | bytes | None], None]) -> None:
                send(SansIOHttpResponse('text/plain'))
                send(b'hello')
                self.received = []

                def continue_protocol():
                    sleep(0.1)
                    send(b' world!')
                    send(None)

                request_thread = threading.Thread(target=continue_protocol)
                request_thread.start()

            def receive(self, data: bytes | None) -> None:
                self.received.append(data)

        protocol = SimpleProtocol()

        webserver.set_http_route(SansIOHttpRoute('/route1', lambda req: protocol)).start_listen()

        url = webserver.localhost_url()

        # WHEN
        actual_response = sync_fetch_response(url + '/route1', method='POST', data='post-body')

        # THEN
        assert actual_response == HttpResponse('hello world!', 'text/plain')
        assert protocol.received == [b'post-body', None]
