from playwright.sync_api import expect

from tests import for_all_webservers
from .page_fixture import Fixture, fixture


@for_all_webservers()
def test_combo(fixture: Fixture):
    # language=python
    fixture.start_remote("""
from wwwpy.remote.designer.ui.searchable_combobox2 import SearchableComboBox
import js
from js import document
target = SearchableComboBox()
document.body.innerHTML = ''
document.body.append(target.element)    
target.placeholder = 'target-placeholder1'
    """)
    page = fixture.page

    # expect(page.get_by_text("foo123")).to_be_attached()
    # await expect(page.locator('input#my-input')).toHaveValue('1');
    # expect(page.locator('input')).to_have_value('foo123')
    locator = page.get_by_placeholder("target-placeholder1")
    expect(locator).to_have_value("")
    fixture.evaluate("import remote")
    fixture.evaluate("remote.target.text_value = 'foo123'")
    expect(locator).to_have_value("foo123")
    return
    locator = page.locator('input[value=""]')
    expect(locator).to_have_count(1)
    return
    page.locator("#root").locator("")
    assert False, page.locator("#root").inner_html()
    # expect(page.locator('body')).to_have_js_property()
    # fixture.evaluate("import remote; remote.target.text_value = 'foo123'")
    # expect(page.locator('body')).to('ready')
    # assert False, page.locator('head').inner_html()
    # fixture.assert_evaluate("False, 'see if it shows'")
