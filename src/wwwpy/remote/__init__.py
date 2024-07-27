def dict_to_js(o):
    import js
    import pyodide
    return pyodide.ffi.to_js(o, dict_converter=js.Object.fromEntries)


async def micropip_install(package):
    from js import pyodide
    await pyodide.loadPackage('micropip')
    import micropip
    await micropip.install([package])
