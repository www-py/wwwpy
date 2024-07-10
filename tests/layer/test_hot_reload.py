"""PYTEST_DONT_REWRITE"""
from pathlib import Path

from playwright.sync_api import Page, expect

from tests import for_all_webservers, restore_sys_path
from wwwpy.server import configure
from wwwpy.webserver import Webserver


@for_all_webservers()
def test_hot_reload__modified(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text("from js import document;document.body.innerHTML = 'ready'")
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('ready')
    # time.sleep(2)
    # change server side file, should reflect on the client side
    remote_init.write_text("from js import document;document.body.innerHTML = 'modified'")
    expect(page.locator('body')).to_have_text('modified')


@for_all_webservers()
def dis_test_hot_reload__created(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    remote = tmp_path / 'remote'
    remote.mkdir()

    (remote / '__init__.py').write_text(_created_python)
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('body')).to_have_text('ready')

    (remote / 'component1.py').write_text("from js import document;document.body.innerHTML = 'created'")
    expect(page.locator('body')).to_have_text('created')


# language=python

_created_python = """
try:
    import component1
except:
    pass    
    
from js import document
document.body.innerHTML = 'ready'
"""
