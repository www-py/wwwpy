from pathlib import Path
from time import sleep

from playwright.sync_api import Page, expect

from tests import for_all_webservers
from wwwpy.bootstrap import bootstrap_routes
from wwwpy.resources import library_resources
from wwwpy.server import configure
from wwwpy.webserver import Webserver
from wwwpy.websocket import WebsocketPool, PoolEvent, Change

file_parent = Path(__file__).parent
layer_5_rpc_server = file_parent / 'layer_5_support/rpc_server'


class TestServerRpc:

    @for_all_webservers()
    def test_rpc(self, page: Page, webserver: Webserver):
        configure.convention(layer_5_rpc_server, webserver)
        webserver.start_listen()

        page.goto(webserver.localhost_url())
        expect(page.locator('body')).to_have_text('42')

    @for_all_webservers()
    def test_rpc_issue_double_load(self, page: Page, webserver: Webserver):
        # related to the stubber to being loaded twice
        configure.convention(layer_5_rpc_server, webserver)
        webserver.start_listen()

        page.goto(webserver.localhost_url())
        expect(page.locator('body')).to_have_text('42')

        page.goto(webserver.localhost_url())
        expect(page.locator('body')).to_have_text('42')


class TestWebsocketRoute:

    @for_all_webservers()
    def test_server_to_remote_message(self, page: Page, webserver: Webserver):
        # language=python
        python_code = """

from js import document, WebSocket
document.body.innerHTML = ''

def log(msg):
    document.body.innerHTML += f'|{msg}'

es = WebSocket.new(f'ws://127.0.0.1:$(webserver.port)/ws')
es.onopen = lambda e: log('open')
es.onmessage = lambda e: log(f'message:{e.data}')        
        """

        python_code = python_code.replace('$(webserver.port)', str(webserver.port))
        webserver.set_http_route(*bootstrap_routes(resources=[library_resources()], python=python_code))
        ws_pool = WebsocketPool('/ws')
        webserver.set_http_route(ws_pool.http_route).start_listen()

        page.goto(webserver.localhost_url())

        expect(page.locator('body')).to_have_text('|open')
        [sleep(0.1) for _ in range(100) if len(ws_pool.clients) == 0]
        assert len(ws_pool.clients) == 1
        client = ws_pool.clients[0]
        client.send('42')
        expect(page.locator('body')).to_have_text('|open|message:42')
        client.send('11')
        expect(page.locator('body')).to_have_text('|open|message:42|message:11')

    @for_all_webservers()
    def test_pool_change(self, page: Page, webserver: Webserver):
        # language=python
        python_code = """

from js import document, WebSocket
document.body.innerHTML = ''
def log(msg):
    document.body.innerHTML += f'|{msg}'

es = WebSocket.new(f'ws://127.0.0.1:$(webserver.port)/ws')

def message(msg):
    log(f'message:{msg}')
    es.close()
    
es.onopen = lambda e: log('open')
es.onmessage = lambda e: message(e.data)        
                """

        python_code = python_code.replace('$(webserver.port)', str(webserver.port))
        webserver.set_http_route(*bootstrap_routes(resources=[library_resources()], python=python_code))

        changes = []

        ws_pool = WebsocketPool('/ws', lambda event: changes.append(event.change))
        webserver.set_http_route(ws_pool.http_route).start_listen()

        page.goto(webserver.localhost_url())

        expect(page.locator('body')).to_have_text('|open')
        assert changes == [Change.add]
        [sleep(0.1) for _ in range(100) if len(ws_pool.clients) == 0]
        assert len(ws_pool.clients) == 1
        client = ws_pool.clients[0]
        client.send('close')
        expect(page.locator('body')).to_have_text('|open|message:close')
        assert changes == [Change.add, Change.remove]

    @for_all_webservers()
    def test_remote_to_server_message(self, page: Page, webserver: Webserver):
        # language=python
        python_code = """
from js import WebSocket
es = WebSocket.new(f'ws://127.0.0.1:$(webserver.port)/ws')    
es.onopen = lambda e: [es.send('foo1'), es.close()]
                """

        python_code = python_code.replace('$(webserver.port)', str(webserver.port))
        webserver.set_http_route(*bootstrap_routes(resources=[library_resources()], python=python_code))
        incoming_messages = []

        def before_change(change: PoolEvent):
            if change.add:
                change.endpoint.listeners.append(lambda msg: incoming_messages.append(msg))

        ws_pool = WebsocketPool('/ws', before_change)
        webserver.set_http_route(ws_pool.http_route).start_listen()

        page.goto(webserver.localhost_url())

        [sleep(0.1) for _ in range(100) if len(incoming_messages) != 2]
        assert len(incoming_messages) == 2
        assert incoming_messages == ['foo1', None]
