from pathlib import Path
from typing import Optional

from playwright.sync_api import Page, expect

from tests import for_all_webservers
from wwwpy.bootstrap import get_javascript_for, wrap_in_tryexcept
from wwwpy.http_response import HttpResponse
from wwwpy.http_route import HttpRoute
from wwwpy.resource_iterator import from_filesystem, PathResource, default_item_filter, Resource
from wwwpy.webserver import Webserver


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


parent = Path(__file__).parent


class Test_ResourceIterator_from_filesystem:
    support_data = parent / 'support_data/from_filesystem'

    def test_one_file(self):
        folder = self.support_data / 'one_file'
        actual = set(from_filesystem(folder))
        expect = {PathResource('foo.py', folder / 'foo.py')}
        assert expect == actual

    def test_zero_file(self):
        folder = self.support_data / 'zero_file'
        folder.mkdir(exist_ok=True)  # git does not commit empty folders
        actual = set(from_filesystem(folder))
        expect = set()
        assert expect == actual

    def test_selective(self):
        folder = self.support_data / 'relative_to'
        actual = set(from_filesystem(folder / 'yes', relative_to=folder))
        expect = {PathResource('yes/yes.txt', folder / 'yes/yes.txt')}
        assert expect == actual

    def test_item_filter(self):
        folder = self.support_data / 'item_filter'
        reject = folder / 'yes/reject'

        pycache = folder / 'yes/__pycache__'
        pycache.mkdir(exist_ok=True)
        (pycache / 'cache.txt').write_text('some cache')

        def item_filter(item: Resource) -> Optional[Resource]:
            if item.filepath == reject:
                return None
            return default_item_filter(item)

        actual = set(from_filesystem(folder, item_filter=item_filter))
        expect = {PathResource('yes/yes.txt', folder / 'yes/yes.txt')}
        assert expect == actual
