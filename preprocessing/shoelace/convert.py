import json
from pathlib import Path
from typing import List

from wwwpy.common.designer import element_library as el
from wwwpy.common.rpc import serialization


def main():
    jet_json, vsc_json = load_jsons()

    assert len(jet_json) == len(vsc_json)

    elements: list[el.ElementDef] = []
    for jet, vsc in zip(jet_json, vsc_json):
        element = create_element(jet, vsc)
        elements.append(element)

    print(serialization.to_json(elements, List[el.ElementDef]))


def create_element(jet, vsc):
    tag_name = jet['name']
    assert tag_name == vsc['name']

    help = el.Help(jet['description'], jet['doc-url'])
    attributes: list[el.AttributeDef] = []
    for jet_attr, vsc_attr in zip(jet['attributes'], vsc['attributes']):
        attr_name = jet_attr['name']
        assert attr_name == vsc_attr['name']
        jet_value = jet_attr.get('value')
        jet_default = jet_value.get('default')
        jet_type = jet_value.get('type')
        values = ['true', 'false'] if jet_type == 'boolean' else \
            [dic['name'] for dic in (vsc_attr['values'])]

        attr = el.AttributeDef(attr_name, help=el.Help('', jet_attr.get('description', ''))
                               , values=values, default_value=jet_default)

        attributes.append(attr)

    events: list[el.EventDef] = []
    for jet_event in jet['events']:
        event_name = jet_event['name']
        event = el.EventDef(event_name, help=el.Help('', jet_event.get('description', '')))
        events.append(event)

    element = el.ElementDef(tag_name, 'js.HTMLElement', help=help,
                            attributes=attributes, events=events)
    return element


def load_jsons():
    parent = Path(__file__).parent
    jetbrains_file = parent / 'web-types.json'
    vscode_file = parent / 'vscode.html-custom-data.json'
    jet_json = load(jetbrains_file)['contributions']['html']['elements']
    vsc_json = load(vscode_file)['tags']
    return jet_json, vsc_json


def load(file):
    return json.loads(file.read_text())


if __name__ == '__main__':
    main()
