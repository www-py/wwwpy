from js import document


async def main():
    from . import component1  # for component registration
    document.body.innerHTML = '<component-1></component-1>'
