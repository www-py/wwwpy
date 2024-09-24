from __future__ import annotations

from inspect import iscoroutinefunction

import js
from js import console

import wwwpy.common.reloader as reloader
from wwwpy.common import _no_remote_infrastructure_found_text
from wwwpy.common.tree import print_tree
from wwwpy.remote import set_timeout
from wwwpy.remote.designer.dev_mode import _setup_browser_dev_mode
from wwwpy.remote.root_path import _get_dir
from wwwpy.remote.websocket import setup_websocket


async def entry_point(dev_mode: bool = False):
    # from wwwpy.common.tree import print_tree
    # print_tree('/wwwpy_bundle')

    await setup_websocket()
    if dev_mode:
        await _setup_browser_dev_mode()

    await _invoke_browser_main()


def _reload():
    async def reload():
        import wwwpy.common.modlib as modlib
        console.log('reloading')
        for package in ['remote', 'common']:
            directory = modlib._find_package_directory(package)
            if directory:
                reloader.unload_path(str(directory))
        await _invoke_browser_main(True)

    set_timeout(reload)


async def _invoke_browser_main(reload=False):
    console.log('invoke_browser_main')
    try:
        js.document.body.innerHTML = f'Going to import remote (reload={reload})'
        import remote
        if reload:
            import importlib
            importlib.reload(remote)
    except ImportError as e:
        import traceback
        msg = _no_remote_infrastructure_found_text + ' Exception: ' + str(e) + '\n\n' + traceback.format_exc() + '\n\n'
        js.document.body.innerHTML = msg.replace('\n', '<br>')
        return

    if hasattr(remote, 'main'):
        if iscoroutinefunction(remote.main):
            await remote.main()
        else:
            remote.main()
