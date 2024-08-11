from __future__ import annotations

from wwwpy.remote import rpc as rpc
from js import console


async def _setup_browser_dev_mode():
    from wwwpy.remote import micropip_install
    from wwwpy.common import designer
    for package in designer.pypi_packages:
        await micropip_install(package)

    def file_changed(event_type: str, filename: str, content: str):
        from wwwpy.remote.root_path import _get_dir
        f = _get_dir().root / filename
        reload = True
        if event_type == 'deleted':
            f.unlink(missing_ok=True)
        elif not f.exists() or f.read_text() != content:
            if not f.parent.exists():
                f.parent.mkdir(parents=True)
            f.write_text(content)
        else:
            reload = False

        content_piece = '' if content is None else f', content_len={len(content)} content=`{content[:100]}`'
        console.log(f'reload={reload} et={event_type} filename={filename}' + content_piece)

        if reload:
            from wwwpy.remote.browser_main import _reload
            _reload()

    rpc.file_changed_listeners_add(file_changed)
