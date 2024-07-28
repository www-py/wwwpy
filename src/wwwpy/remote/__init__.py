from __future__ import annotations

from typing import Callable, Union, Awaitable


def dict_to_js(o):
    import js
    import pyodide
    return pyodide.ffi.to_js(o, dict_converter=js.Object.fromEntries)


async def micropip_install(package):
    from js import pyodide
    await pyodide.loadPackage('micropip')
    import micropip
    await micropip.install([package])


def set_timeout(callback: Callable[[], Union[None, Awaitable[None]]], timeout_millis: int | None = 0):
    from pyodide.ffi import create_once_callable
    from js import window
    window.setTimeout(create_once_callable(callback), timeout_millis)
