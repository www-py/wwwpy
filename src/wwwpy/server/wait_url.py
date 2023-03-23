import urllib.error
import urllib.request
from time import sleep


def wait_url(url: str) -> None:
    for _ in range(300):
        try:
            urllib.request.urlopen(url)
            return
        except urllib.error.HTTPError:
            return
        except Exception:
            sleep(0.01)
    raise Exception(f'timeout wait_url(`{url}`)')
