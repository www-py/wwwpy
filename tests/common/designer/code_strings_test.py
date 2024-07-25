from wwwpy.common.designer.code_strings import html_string_edit


def test_html_edit():
    common_piece = '''
import wwwpy.remote.component as wpc
# comment1
class MyElement(wpc.Component): # comment2
    btn1: HTMLButtonElement = wpc.element()
    def connectedCallback(self):        
        self.element.innerHTML = """
        <div>my-element5 a</div>
        <button data-name='btn1'>list async tasks</button>
        '''

    original_source = common_piece + '"""'
    exepct_source = common_piece + '''<button data-name='btn2'>list files in folder</button>"""'''

    def manipulate_html(html):
        return html + "<button data-name='btn2'>list files in folder</button>"

    actual_source = html_string_edit(original_source, manipulate_html)

    assert actual_source == exepct_source
