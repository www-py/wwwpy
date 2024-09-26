import asyncio
import sys
import traceback
from inspect import iscoroutinefunction
from threading import Thread


def unasync(f):
    if not iscoroutinefunction(f):
        return f
    result = None
    exc_info = None
    exception = None

    async def main_safe(*args, **kwargs):
        nonlocal result, exc_info, exception
        result = None
        exc_info = None
        exception = None
        try:
            result = await f(*args, **kwargs)
        except Exception as ex:
            exception = ex
            exc_info = sys.exc_info()

    def start(*args, **kwargs):
        asyncio.run(main_safe(*args, **kwargs))

    def wrapper(*args, **kwargs):
        nonlocal result, exc_info, exception
        thread = Thread(target=start, args=args, kwargs=kwargs)
        thread.start()
        thread.join()
        if exc_info is not None:
            exc_type, exc_value, exc_traceback = exc_info
            print('', file=sys.stderr)
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
            raise exception
        return result

    return wrapper
