from time import sleep

from remote.rpc import Layer5Rpc1
from wwwpy.server.configure import websocket_pool
from wwwpy.websocket import WebsocketPool


def call_remote(msg):
    [sleep(0.1) for _ in range(100) if websocket_pool.clients == 0]
    assert len(websocket_pool.clients) > 0
    client = websocket_pool.clients[0]
    client.rpc(Layer5Rpc1).set_body_inner_html(msg)
