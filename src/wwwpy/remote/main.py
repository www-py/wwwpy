from inspect import iscoroutinefunction

from wwwpy.common.rpc.serializer import RpcRequest


async def entry_point():
    from wwwpy.common.tree import print_tree
    print_tree('/wwwpy_bundle')
    import js
    await setup_websocket()
    try:
        js.document.body.innerHTML = 'Going to import remote'
        import remote
    except ImportError as e:
        import traceback
        msg = 'module remote load failed. Error: ' + str(e) + '\n\n' + traceback.format_exc() + '\n\n'
        js.document.body.innerHTML = msg.replace('\n', '<br>')
        return

    if hasattr(remote, 'main'):
        if iscoroutinefunction(remote.main):
            await remote.main()
        else:
            remote.main()


async def setup_websocket():
    from js import document, WebSocket, window, console

    def log(msg):
        console.log(msg)

    def message(msg):
        log(f'message:{msg}')
        r = RpcRequest.from_json(msg)
        import remote.rpc as rpc
        class_name, func_name = r.func.split('.')
        attr = getattr(rpc, class_name)
        inst = attr()
        func = getattr(inst, func_name)
        func(*r.args)

    l = window.location
    proto = 'ws' if l.protocol == 'http:' else 'wss'
    es = WebSocket.new(f'{proto}://{l.host}/wwwpy/ws')
    es.onopen = lambda e: log('open')
    es.onmessage = lambda e: message(e.data)
