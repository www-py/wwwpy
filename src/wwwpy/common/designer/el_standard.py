from typing import List

from wwwpy.common.designer.element_library import ElementDef, Help, EventDef


def _standard_elements_def() -> List[ElementDef]:
    res = [
        ElementDef(
            'button', 'js.HTMLButtonElement',
            help=Help('A clickable button.', 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button'),
            events=[EventDef('click', Help('The button was clicked.',
                                           'https://developer.mozilla.org/en-US/docs/Web/API/Element/click_event'))],
        ),
        ElementDef(
            'input', 'js.HTMLInputElement',
            help=Help('A field for entering text.', 'https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input'),
            events=[
                EventDef('input', Help('The input event fires when the value of the element has been changed '
                                       'as a direct result of a user action',
                                       'https://developer.mozilla.org/en-US/docs/Web/API/Element/input_event')),
                EventDef('change')
            ]
        ),
        ElementDef(
            'div', 'js.HTMLDivElement',
            help=Help('A generic container element.',
                      'https://developer.mozilla.org/en-US/docs/Web/HTML/Element/div')
        ),

    ]
    for r in res:
        r.gen_html = _generateHtml
    return res


def _generateHtml(element_def: ElementDef, name: str) -> str:
    tag_name = element_def.tag_name

    def _def(placeHolder=False, add=''):
        def inner():
            pl = '' if not placeHolder else f' placeholder="{name}"'
            add1 = '' if not add else f' {add}'
            return f'<{tag_name} data-name="{name}"{pl}{add1}>{name}</{tag_name}>'

        return inner

    func = {
        'button': _def(),
    }
    gen_html = func.get(tag_name, None)
    html = '\n' + gen_html() if gen_html else '' + ElementDef.default_gen_html(element_def, name)
    return html


# [
#     _comp('input', 'js.HTMLInputElement', '<input type="text" data-name="#name#" value="#name#">'),
#     _comp('button', 'js.HTMLButtonElement', '<button data-name="#name#">#name#</button>'),
#     _comp('textarea', 'js.HTMLTextAreaElement', '<textarea data-name="#name#">#name#</textarea>'),
#     _comp('select', 'js.HTMLSelectElement',
#           '<select data-name="#name#"><option>#name#</option></select>'),
#     _comp('div', 'js.HTMLDivElement', '<div data-name="#name#">#name#</div>'),
#     _comp('p', 'js.HTMLParagraphElement', '<p data-name="#name#">#name#</p>'),
#     _comp('h1', 'js.HTMLHeadingElement', '<h1 data-name="#name#">#name#</h1>'),
#     _comp('h2', 'js.HTMLHeadingElement', '<h2 data-name="#name#">#name#</h2>'),
#     _comp('h3', 'js.HTMLHeadingElement', '<h3 data-name="#name#">#name#</h3>'),
#     _comp('a', 'js.HTMLAnchorElement', '<a href="#" data-name="#name#">#name#</a>'),
#     _comp('img', 'js.HTMLImageElement', '<img src="#" alt="#name#" data-name="#name#">'),
#     _comp('ul', 'js.HTMLUListElement', '<ul data-name="#name#"><li>#name#</li></ul>'),
#     _comp('ol', 'js.HTMLOListElement', '<ol data-name="#name#"><li>#name#</li></ol>'),
#     _comp('li', 'js.HTMLLIElement', '<li data-name="#name#">#name#</li>'),
#     _comp('table', 'js.HTMLTableElement', '<table data-name="#name#"><tr><td>#name#</td></tr></table>'),
#     _comp('form', 'js.HTMLFormElement', '<form data-name="#name#">#name#</form>'),
#     _comp('label', 'js.HTMLLabelElement', '<label data-name="#name#">#name#</label>'),
#
# ]