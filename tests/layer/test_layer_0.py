from __future__ import annotations

from tests import for_all_webservers
from wwwpy.http_request import HttpRequest
from wwwpy.http_response import HttpResponse
from wwwpy.http_route import HttpRoute
from wwwpy.server import find_port
from wwwpy.server.fetch import sync_fetch_response
from wwwpy.webserver import Webserver


@for_all_webservers()
def test_webservers_get(webserver: Webserver):
    response_a = HttpResponse('a', 'text/plain')
    response_b = HttpResponse('b', 'text/html')

    webserver.set_http_route(HttpRoute('/b', lambda req: response_b))
    webserver.set_http_route(HttpRoute('/', lambda req: response_a))

    webserver.set_port(find_port()).start_listen()

    url = webserver.localhost_url()

    assert sync_fetch_response(url) == response_a
    assert sync_fetch_response(url + '/b') == response_b


@for_all_webservers()
def test_webservers_post(webserver: Webserver):
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
