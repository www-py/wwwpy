from time import sleep

from tests import for_all_webservers
from playwright.sync_api import Page, expect

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
