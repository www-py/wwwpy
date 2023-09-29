from js import fetch


async def async_fetch_str(url: str, method: str = 'GET', data: str = '') -> str:
    print(f'url={url}')
    print(f'method={method}')
    print(f'data=`{data}`')
    response = await fetch(url, method=method, body=data)
    text = await response.text()
    return text
