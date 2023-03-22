from tests import for_all_webservers
from wwwpy import Response, Routes, Webserver
from wwwpy.response import Request
from wwwpy.server import find_port
from wwwpy.server.fetch import sync_fetch_response


@for_all_webservers()
def test_webservers_get(webserver: Webserver):
    response_a = Response('a', 'text/plain')
    response_b = Response('b', 'text/html')

    routes = (
        Routes()
        .add_route('/b', lambda req: response_b)
        .add_route('/', lambda req: response_a)
    )

    webserver.set_routes(routes).set_port(find_port()).start_listen().wait_ready()

    url = webserver.localhost_url()

    assert sync_fetch_response(url) == response_a
    assert sync_fetch_response(url + '/b') == response_b


@for_all_webservers()
def test_webservers_post(webserver: Webserver):
    # GIVEN
    response_a = Response('a', 'text/plain')
    actual_request: Request = None

    def handler(req: Request) -> Response:
        nonlocal actual_request
        actual_request = req
        return response_a

    routes = Routes().add_route('/rpc', handler)

    webserver.set_routes(routes).set_port(find_port()).start_listen().wait_ready()

    url = webserver.localhost_url()

    # WHEN
    actual_response = sync_fetch_response(url + '/rpc', method='POST', data='post-body')

    # THEN
    assert actual_response == response_a
    assert actual_request.method == 'POST'
    assert actual_request.content.decode('utf8') == 'post-body'
