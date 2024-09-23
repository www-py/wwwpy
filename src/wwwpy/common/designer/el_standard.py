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
