from js import document, HTMLElement, Event

from wwwpy.remote.component import Component, Metadata, attribute, element
import wwwpy.remote.component as wpc


def test_component_metadata():
    class Comp1(Component, metadata=Metadata('comp-1')): ...

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
    class Comp1(Component, metadata=Metadata('tag-1')): ...

    assert Comp1.component_metadata.clazz == Comp1
    assert Comp1.component_metadata.tag_name == 'tag-1'
    assert Comp1.component_metadata.registered


def test_define_custom_metadata__auto_define_False():
    class Comp1(Component, metadata=Metadata('tag-1', auto_define=False)): ...

    assert not Comp1.component_metadata.registered


def test_no_custom_metadata__auto_define_True():
    class Comp1(Component): ...

    assert Comp1.component_metadata.registered


def test_document_tag_creation():
    class Comp2(Component):

        def init_component(self):
            self.element.attachShadow(to_js({'mode': 'open'}))
            self.element.shadowRoot.innerHTML = '<h1>hello123</h1>'

    ele = document.createElement(Comp2.component_metadata.tag_name)
    # import js
    # js.console.log(ele)
    # setattr(js.window,'ciccio',ele)
    # js.eval('debugger;')
    # count = 0
    # for _ in range(100000):
    #     count += 1
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

    class Comp4(Component, metadata=Metadata('comp-4')):
        text = attribute()

        def attributeChangedCallback(self, name, oldValue, newValue):
            calls.append((name, oldValue, newValue))

    comp = Comp4()
    comp.text = 'abc'

    assert calls == [('text', None, 'abc')]
    calls.clear()

    comp.element.setAttribute('text', 'def')
    assert calls == [('text', 'abc', 'def')]


def test_redefining_an_element_should_be_ok():
    class Comp10a(Component, metadata=Metadata('comp-10')):
        pass

    class Comp10b(Component, metadata=Metadata('comp-10')):
        pass


def test_redefined_element_should_be_ok():
    class Comp9a(Component, metadata=Metadata('comp-9')):
        attr1 = attribute()

        def attributeChangedCallback(self, name: str, oldValue: str, newValue: str):
            self.element.innerHTML = f'Comp9a'

    comp = document.createElement('comp-9')
    comp.setAttribute('attr1', 'x')
    assert 'Comp9a' == comp.innerHTML

    class Comp9b(Component, metadata=Metadata('comp-9')):
        attr1 = attribute()

        def attributeChangedCallback(self, name: str, oldValue: str, newValue: str):
            self.element.innerHTML = f'Comp9b'

    comp = document.createElement('comp-9')
    comp.setAttribute('attr1', 'x')
    assert 'Comp9b' == comp.innerHTML


class TestElementAttribute:

    def test_HTMLElement_attribute(self):
        class Comp5(Component):
            div1: HTMLElement = element()
            foo1: HTMLElement = element()

            def init_component(self):
                self.element.innerHTML = '<div data-name="div1">789</div>'

        comp = Comp5()
        assert comp.div1.innerHTML == '789'

        try:
            foo1 = comp.foo1
            assert False, 'Should raise AttributeError'
        except AttributeError:
            pass

    def test_Component_attribute(self):
        class Comp6(Component, metadata=Metadata('comp-6')):
            div1: HTMLElement = element()

            def init_component(self):
                self.element.innerHTML = '<div data-name="div1">abc</div>'

        class Comp7(Component):
            c6: Comp6 = element()

            def init_component(self):
                self.element.innerHTML = '<comp-6 data-name="c6"></comp-6>'

        comp7 = Comp7()
        assert comp7.c6.div1.innerHTML == 'abc'

    def test_Component_attribute_type(self):
        class CompUnused(Component):
            ...

        class CompWrongType(Component):
            c6: CompUnused = element()  # this is actually a Comp6!

            def init_component(self):
                self.element.innerHTML = '<comp-6 data-name="c6"></comp-6>'

        try:
            comp = CompWrongType()
            nop = comp.c6
            assert False, 'Should raise a TypeError'
        except TypeError:
            pass

    def test_define_new_root(self):
        class Comp8(Component):
            root: HTMLElement
            div1: HTMLElement = element()

            def root_element(self):
                return self.root

            def init_component(self):
                self.root = document.createElement('div')
                self.root.innerHTML = '<div data-name="div1">root</div>'

        comp = Comp8()
        assert comp.div1.innerHTML == 'root'


class TestElementEventBinding:

    def test_simple_bind(self):
        actual = []

        class Comp1(Component):
            def init_component(self):
                self.element.innerHTML = "<button data-name='foo'>foo</button>"

            def foo__click(self, *args):
                actual.append(1)

        target = Comp1()
        foo = target.element.querySelector(f'[data-name="foo"]')
        foo.click()
        assert [1] == actual

    def test_underscore_in_event_is_seen_as_dash(self):
        actual = []

        class Comp1(Component):
            def init_component(self):
                self.element.innerHTML = "<button data-name='foo'>foo</button>"

            def foo__custom_1(self, *args):
                actual.append(1)

        target = Comp1()
        foo = target.element.querySelector(f'[data-name="foo"]')
        foo.dispatchEvent(Event.new('custom-1'))
        assert [1] == actual


def to_js(o):
    import js
    import pyodide
    return pyodide.ffi.to_js(o, dict_converter=js.Object.fromEntries)
