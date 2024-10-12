from time import sleep

from playwright.sync_api import expect

from tests import for_all_webservers, timeout_multiplier
from tests.server.page_fixture import PageFixture, fixture
from wwwpy.common.quickstart import is_empty_project


@for_all_webservers()
def test_dev_mode_with_empty_project__should_show_quickstart_dialog(fixture: PageFixture):
    fixture.dev_mode = True
    assert list(fixture.tmp_path.iterdir()) == []
    fixture.start_remote()

    expect(fixture.page.locator('wwwpy-dev-mode')).to_be_attached()
    # language=python

    fixture.assert_evaluate_retry("""
from wwwpy.remote.designer.ui.dev_mode_component import DevModeComponent
DevModeComponent.instance.quickstart_visible()
""")
    assert list(fixture.tmp_path.iterdir()) == []
    assert is_empty_project(fixture.tmp_path)

    #         from wwwpy.common import quickstart
    #         quickstart._check_quickstart(directory)