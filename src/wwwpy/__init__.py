try:
    from importlib.metadata import version

    __version__ = version(__name__)
    del version
except:
    __version__ = 'unknown'

try:
    from wwwpy import build_meta
except ImportError:
    pass
