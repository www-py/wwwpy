from time import sleep

from remote.rpc import Layer5Rpc1
from wwwpy.websocket import WebsocketPool


def call_remote():
    websocket_pool: WebsocketPool = None
    [sleep(0.1) for _ in range(100) if websocket_pool.clients == 0]
    client = websocket_pool.clients[0]

