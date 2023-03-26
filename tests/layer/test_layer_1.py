from time import sleep

from tests import for_all_webservers
from playwright.sync_api import Page, expect

from wwwpy.bootstrap import get_javascript_for, wrap_in_tryexcept
from wwwpy.http_response import HttpResponse
from wwwpy.http_route import HttpRoute
from wwwpy.webserver import Webserver


@for_all_webservers()
def test_javascript_execution(page: Page, webserver: Webserver):
    html = '<html><head></head><body><script>document.head.id = "id1";</script></body></html>'
    webserver.set_http_route(HttpRoute('/', lambda request: HttpResponse.text_html(html)))
    webserver.start_listen()
    page.goto(webserver.localhost_url())
    expect(page.locator('id=id1')).to_have_id('id1')


@for_all_webservers()
def test_python_execution(page: Page, webserver: Webserver):
    python_code = 'from js import document\ndocument.getElementById("tag1").value = "foo1"'
    javascript = get_javascript_for(python_code)
    html = f'<input id="tag1" value="bar"><script>{javascript}</script>'
    webserver.set_http_route(HttpRoute('/', lambda request: HttpResponse.text_html(html)))
    webserver.start_listen()
    page.goto(webserver.localhost_url())
    expect(page.locator('id=tag1')).to_have_value('foo1')


def test_python_code_execution():
    tmp = []
    code = wrap_in_tryexcept('1/0', (
        'tmp.append("executed")\n'
        'tmp.append("type=" + str(type(exception).__name__))'
    ))
    exec(code)
    assert ['executed', 'type=ZeroDivisionError'] == tmp
