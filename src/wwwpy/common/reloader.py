def reload(module):
    import importlib
    # importlib.invalidate_caches()
    return importlib.reload(module)


def find_package_location(package_name):
    import importlib.util
    spec = importlib.util.find_spec(package_name)
    return spec.origin if spec else None
