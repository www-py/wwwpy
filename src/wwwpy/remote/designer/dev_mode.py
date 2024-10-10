from __future__ import annotations

import sys

_wwwpy_dev_mode = 'wwwpy_dev_mode'


async def activate():
    setattr(sys, _wwwpy_dev_mode, True)
    from wwwpy.remote import micropip_install
    from wwwpy.common import designer

    for package in designer.pypi_packages:
        await micropip_install(package)

def is_active() -> bool:
    return hasattr(sys, _wwwpy_dev_mode)
