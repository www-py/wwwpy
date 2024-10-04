from time import sleep

from playwright.sync_api import expect

from tests import for_all_webservers, timeout_multiplier
from tests.server.remote_ui.page_fixture import fixture, Fixture
from wwwpy.unasync import unasync


@for_all_webservers()
def test_hot_reload__modified(fixture: Fixture):
    fixture.dev_mode = True
    fixture.start_remote("""from js import document;document.body.innerHTML = '<input id="tag1" value="ready">'""")

    expect(fixture.page.locator('id=tag1')).to_have_value('ready')

    # change server side file, should reflect on the client side
    fixture.remote_init.write_text("""import js; js.document.body.innerHTML = '<input id="tag1" value="modified">'""")
    expect(fixture.page.locator('id=tag1')).to_have_value('modified')


@for_all_webservers()
def test_hot_reload__created(fixture: Fixture):
    fixture.dev_mode = True
    fixture.start_remote(_created_python)
    expect(fixture.page.locator('id=msg1')).to_have_value('exists=False')

    (fixture.remote / 'component1.py').write_text(
        "import js; js.console.log('comp1!')\n" +
        """js.document.body.innerHTML = '<input id="tag1" value="import ok">'""")
    expect(fixture.page.locator('id=msg1')).to_have_value('exists=True')


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
def test_hot_reload__deleted(fixture: Fixture):
    fixture.dev_mode = True
    fixture.remote.mkdir()
    file1 = fixture.remote / 'file1.txt'
    file1.write_text('hello')

    fixture.start_remote(
        # language=python
        """from pathlib import Path; from js import document
file1_txt = Path(__file__).parent / 'file1.txt'
document.body.innerHTML = f'<input id="msg1" value="exists={str(file1_txt.exists())}">'
""")

    expect(fixture.page.locator('id=msg1')).to_have_value('exists=True')

    file1.unlink()
    expect(fixture.page.locator('id=msg1')).to_have_value('exists=False')


class TestServerRpcHotReload:

    @for_all_webservers()
    def test_server_rpc_body_change(self, fixture: Fixture):
        # GIVEN
        fixture.dev_mode = True
        fixture.write_module('server/rpc.py', "async def func1() -> str: return 'ready'")

        fixture.start_remote(  # language=python
            """
async def main():
    import js 
    from server import rpc 
    js.document.body.innerText = 'first=' + await rpc.func1()
""")

        expect(fixture.page.locator('body')).to_have_text('first=ready', use_inner_text=True)

        # WHEN
        fixture.write_module('server/rpc.py', "async def func1() -> str: return 'updated'")
        self._wait_filesystem_debounce_and_hotreload()
        fixture.remote_init.write_text(fixture.remote_init.read_text().replace('first=', 'second='))

        # THEN
        expect(fixture.page.locator('body')).to_have_text('second=updated', use_inner_text=True)

    @for_all_webservers()
    def test_server_rpc__call_another_file(self, fixture: Fixture):
        # GIVEN
        fixture.dev_mode = True
        fixture.write_module('server/database.py', "conn_name = 'conn1'")
        fixture.write_module('server/rpc.py',
                             "from . import database as db\n"
                             "async def func1() -> str: res = 'conn:'+db.conn_name; print(f'res={res}\\n'); return res")

        fixture.start_remote(  # language=python
            """
async def main():
    import js 
    from server import rpc 
    js.document.body.innerText = 'first=' + await rpc.func1()
""")
        expect(fixture.page.locator('body')).to_have_text('first=conn:conn1', use_inner_text=True)

        # WHEN
        fixture.write_module('server/database.py', "conn_name = 'conn1-updated'")
        self._wait_filesystem_debounce_and_hotreload()
        # todo server/rpc should hold any request up until hotreload is finished
        fixture.remote_init.write_text(fixture.remote_init.read_text().replace('first=', 'second='))

        # THEN
        expect(fixture.page.locator('body')).to_have_text('second=conn:conn1-updated', use_inner_text=True)

    def _wait_filesystem_debounce_and_hotreload(self):
        # todo, awful: wait the debounce of file system events/hotreload
        sleep(0.2 * timeout_multiplier())
