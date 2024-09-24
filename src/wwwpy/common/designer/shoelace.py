from pathlib import Path
from typing import List

from wwwpy.common.collectionlib import ListMap
from wwwpy.common.designer.element_library import ElementDef, EventDef, Help, NamedListMap
from wwwpy.common.rpc import serialization

parent = Path(__file__).parent


def _reorder(elements: List[ElementDef]):
    order = ['sl-button', 'sl-input', 'sl-textarea', 'sl-select',
             'sl-checkbox', 'sl-dropdown', 'sl-switch', 'sl-progress-bar', 'sl-split-panel',
             'sl-textarea', 'sl-alert', 'sl-drawer']
    order.reverse()
    by_tag_name = {element.tag_name: element for element in elements}
    for o in order:
        ed = by_tag_name.get(o)
        if not ed:
            raise ValueError(f"Element {o} not found")
        elements.remove(ed)
        elements.insert(0, ed)

def _shoelace_elements_def() -> List[ElementDef]:

    shoelace_json = (parent / 'shoelace.json').read_text()
    elements = serialization.from_json(shoelace_json, List[ElementDef])
    elements = ListMap(elements, key_func=lambda x: x.tag_name)
    for element in elements:
        element.gen_html = _shoelaceGenerateHtml
    sl_button = elements.get('sl-button')
    url = "https://developer.mozilla.org/en-US/docs/Web/API/Element/click_event"
    sl_button.events.insert(0, EventDef('click', Help('', url)))
    sl_icon = elements.get('sl-icon')
    sl_icon.attributes.get('name').values = (parent / 'sl_icons.txt').read_text().split('\n')

    _reorder(elements)
    return elements


def _shoelaceGenerateHtml(element_def: ElementDef, name: str) -> str:
    tag_name = element_def.tag_name

    def _def(placeHolder=False, add=''):
        def inner():
            pl = '' if not placeHolder else f' placeholder="{name}"'
            add1 = '' if not add else f' {add}'
            return f'<{tag_name} data-name="{name}"{pl}{add1}>{name}</{tag_name}>'

        return inner

    func = {
        'sl-button': _def(),
        'sl-input': _def(placeHolder=True),
        'sl-textarea': _def(placeHolder=True),
        'sl-select': lambda: f'''<sl-select data-name="{name}" label="Select a Few" value="option-1 option-2 option-3" multiple clearable max-options-visible="0">
                <sl-option value="option-1">Option 1</sl-option>
                <sl-option value="option-2">Option 2</sl-option>
                <sl-option value="option-3">Option 3</sl-option>
                <sl-option value="option-4">Option 4</sl-option>
                <sl-option value="option-5">Option 5</sl-option>
                <sl-option value="option-6">Option 6</sl-option>
            </sl-select>''',
        'sl-checkbox': _def(),
        'sl-radio': _def(),
        'sl-switch': _def(),
        'sl-alert': _def(add='type="info"'),
        'sl-badge': _def(),
        'sl-card': lambda: f'''<sl-card data-name="{name}"><div slot="header">{name}</div><div slot="footer">Footer</div></sl-card>''',
        'sl-dialog': lambda: f'''<sl-dialog data-name="{name}" label="{name}" open><sl-button slot="footer" variant="primary">Close</sl-button></sl-dialog>''',
        'sl-drawer': lambda: f'''<sl-drawer data-name="{name}" open label="Drawer" placement="end" class="drawer-placement-start">
    <span>Drop elements here.<br>To close the drawer with Python set {name}.open=False<br>In html, remove the attribute `open`</span>
</sl-drawer>''',
        'sl-dropdown': lambda: f'''<sl-dropdown data-name="{name}"><sl-button slot="trigger" caret>{name}</sl-button><sl-menu><sl-menu-item>Item 1</sl-menu-item></sl-menu></sl-dropdown>''',
        'sl-tooltip': lambda: f'''<sl-tooltip data-name="{name}" content="{name}"><sl-button>Hover Me</sl-button></sl-tooltip>''',
        'sl-progress-bar': _def(add='value="50"'),
        'sl-image-comparer': lambda: f'''<sl-image-comparer data-name="{name}">
    <img slot="before" src="https://images.unsplash.com/photo-1517331156700-3c241d2b4d83?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=80&sat=-100&bri=-5" alt="Grayscale version of kittens in a basket looking around." />
    <img slot="after" src="https://images.unsplash.com/photo-1517331156700-3c241d2b4d83?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=80" alt="Color version of kittens in a basket looking around." />
</sl-image-comparer>''',
        'sl-skeleton': _def(),
        'sl-spinner': _def(),
        'sl-icon': _def(add='name="star"'),
        'sl-split-panel': lambda: f'''<sl-split-panel position="25">
    <div slot="start" style="height: 200px; background: var(--sl-color-neutral-50); display: flex; align-items: center; justify-content: center; overflow: hidden;">
        <span>Start</span>
    </div>
    <div slot="end" style="height: 200px; background: var(--sl-color-neutral-50); display: flex; align-items: center; justify-content: center; overflow: hidden;">
        <span>End<br>You can change orientation setting the attribute `vertical`</span>
    </div>
</sl-split-panel>''',

    }
    gen_html = func.get(tag_name, None)
    html = '\n' + gen_html() if gen_html else '' + ElementDef.default_gen_html(element_def, name)
    return html
