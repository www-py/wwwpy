from wwwpy.server.configure import websocket_pool

from remote import rpc


async def send_message_to_all(msg: str) -> str:
    for client in websocket_pool.clients:
        client.rpc(rpc.Rpc).new_message(msg)
    return 'done'
