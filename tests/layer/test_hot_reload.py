from pathlib import Path

from playwright.sync_api import Page, expect

from tests import for_all_webservers
from tests.common import restore_sys_path
from wwwpy.server import configure
from wwwpy.webserver import Webserver


@for_all_webservers()
def test_hot_reload__modified(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    remote_init = tmp_path / 'remote' / '__init__.py'
    remote_init.parent.mkdir(parents=True)
    remote_init.write_text("""from js import document;document.body.innerHTML = '<input id="tag1" value="ready">'""")
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('id=tag1')).to_have_value('ready')
    # time.sleep(2)
    # change server side file, should reflect on the client side
    remote_init.write_text("""from js import document;document.body.innerHTML = '<input id="tag1" value="modified">'""")
    expect(page.locator('id=tag1')).to_have_value('modified')


@for_all_webservers()
def test_hot_reload__created(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    remote = tmp_path / 'remote'
    remote.mkdir()

    (remote / '__init__.py').write_text(_created_python)
    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('id=msg1')).to_have_value('exists=False')

    (remote / 'component1.py').write_text(
        "from js import document, console; console.log('comp1!')\n" +
        """document.body.innerHTML = '<input id="tag1" value="import ok">'""")
    expect(page.locator('id=msg1')).to_have_value('exists=True')


# language=python
_created_python = """
from pathlib import Path   
from js import document, console
component1_py = Path(__file__).parent / 'component1.py'
document.body.innerHTML = f'<input id="msg1" value="exists={str(component1_py.exists())}">'
console.log(document.body.innerHTML)
console.log('importing component1')
try:
    import component1
except:
    pass
    
"""


@for_all_webservers()
def test_hot_reload__deleted(page: Page, webserver: Webserver, tmp_path, restore_sys_path):
    remote = tmp_path / 'remote'
    remote.mkdir()

    (remote / '__init__.py').write_text(_deleted_python)
    file1 = remote / 'file1.txt'
    file1.write_text('hello')

    configure.convention(tmp_path, webserver, dev_mode=True)
    webserver.start_listen()

    page.goto(webserver.localhost_url())
    expect(page.locator('id=msg1')).to_have_value('exists=True')

    file1.unlink()
    expect(page.locator('id=msg1')).to_have_value('exists=False')


# language=python
_deleted_python = """
from pathlib import Path   
from js import document
file1_txt = Path(__file__).parent / 'file1.txt'
document.body.innerHTML = f'<input id="msg1" value="exists={str(file1_txt.exists())}">'
"""
