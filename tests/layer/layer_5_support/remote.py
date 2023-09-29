from js import document


async def main():
    from server.rpc import multiply
    res = await multiply(7, 6)
    document.body.innerHTML = str(res)
