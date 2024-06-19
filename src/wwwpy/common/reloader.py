def reload(module):
    import importlib
    # importlib.invalidate_caches()
    return importlib.reload(module)
