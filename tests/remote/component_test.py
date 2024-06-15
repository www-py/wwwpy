from js import document

from wwwpy.remote.component import Component, ComponentMetadata, attribute


def test_component_metadata():
    class Comp1(Component):
        component_metadata = ComponentMetadata('comp-1')

    assert Comp1.component_metadata.clazz == Comp1
    assert 'comp' in Comp1.component_metadata.tag_name


def test_simple_html():
    class Comp1(Component):
        def init_component(self):
            self.element.innerHTML = '<div>hello</div>'
            # beware of https://stackoverflow.com/questions/43836886/failed-to-construct-customelement-error-when-javascript-file-is-placed-in-head !!

    comp1 = Comp1()
    assert 'hello' in comp1.element.innerHTML


def test_define_custom_metadata():
    class Comp1(Component):
        component_metadata = ComponentMetadata('tag-1')

    assert Comp1.component_metadata.clazz == Comp1
    assert Comp1.component_metadata.tag_name == 'tag-1'
    assert Comp1.component_metadata.registered


def test_define_custom_metadata__auto_define_False():
    class Comp1(Component):
        component_metadata = ComponentMetadata('tag-1', auto_define=False)

    assert not Comp1.component_metadata.registered


def test_no_custom_metadata__auto_define_True():
    class Comp1(Component):
        pass

    assert Comp1.component_metadata.registered


def test_document_tag_creation():
    class Comp2(Component):

        def init_component(self):
            self.element.attachShadow(to_js({'mode': 'open'}))
            self.element.shadowRoot.innerHTML = '<h1>hello123</h1>'

    ele = document.createElement(Comp2.component_metadata.tag_name)
    assert 'hello123' in ele.shadowRoot.innerHTML


def test_append_tag_to_document():
    class Comp2(Component):

        def connectedCallback(self):
            self.element.innerHTML = '<h1>hello456</h1>'

    document.body.innerHTML = f'<{Comp2.component_metadata.tag_name}></{Comp2.component_metadata.tag_name}>'
    assert 'hello456' in document.body.innerHTML


def test_observed_attributes__with_default_metadata():
    calls = []

    class Comp3(Component):
        text = attribute()

        def attributeChangedCallback(self, name, oldValue, newValue):
            calls.append((name, oldValue, newValue))

    comp = Comp3()
    comp.text = 'abc'

    assert calls == [('text', None, 'abc')]
    calls.clear()

    comp.element.setAttribute('text', 'def')
    assert calls == [('text', 'abc', 'def')]


def test_observed_attributes__with_custom_metadata():
    calls = []

    class Comp4(Component):
        component_metadata = ComponentMetadata('comp-4')
        text = attribute()

        def attributeChangedCallback(self, name, oldValue, newValue):
            calls.append((name, oldValue, newValue))

    comp = Comp4()
    comp.text = 'abc'

    assert calls == [('text', None, 'abc')]
    calls.clear()

    comp.element.setAttribute('text', 'def')
    assert calls == [('text', 'abc', 'def')]

def to_js(o):
    import js
    import pyodide
    return pyodide.ffi.to_js(o, dict_converter=js.Object.fromEntries)
