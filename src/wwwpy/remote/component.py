from __future__ import annotations

import js
from js import window, HTMLElement
from pyodide.ffi import create_proxy

namespace = "window.python_custom_elements"


class Metadata:
    def __init__(self, tag_name: str | None = None, clazz=None, auto_define=True):
        if clazz is not None:
            if not issubclass(clazz, Component):
                raise Exception(f'clazz must be a subclass of {Component.__name__}')
            if tag_name is None:
                # get the full class name
                fully_qualified_class_name = clazz.__qualname__
                tag_name = ('wwwpy-auto-' + fully_qualified_class_name.lower()
                            .replace('<', '-')
                            .replace('>', '-')
                            .replace('.', '-')
                            )

        self.tag_name = tag_name
        self.observed_attributes = set()
        self.registered = False
        self.clazz = clazz
        self.auto_define = auto_define
        self._custom_element_class_template = None

    def __set_name__(self, owner, name):
        if not issubclass(owner, Component):
            raise Exception(f'attribute {name} must be in a subclass of {Component.__name__}')
        self.clazz = owner
        # if self.auto_define:
        #     self.define_element()

    def define_element(self):
        if self.registered:
            return
        if js.eval(f'typeof {namespace}') == 'undefined':
            js.eval(namespace + ' = {}')

        js_class_name = self.tag_name.replace('-', '_').replace('.', '_')
        self._js_class_name = js_class_name

        pc = js.eval(namespace)
        already_defined = hasattr(pc, js_class_name)
        setattr(pc, js_class_name, self.clazz)  # set the python constructor, in any case
        if not already_defined:
            obs_attr = ', '.join(f'"{attr}"' for attr in self.observed_attributes)
            code = (_custom_element_class_template
                    .replace('$ClassName', js_class_name)
                    .replace('$tagName', self.tag_name)
                    .replace('$observedAttributes', obs_attr)
                    .replace('$namespace', namespace)
                    )
            self._custom_element_class_template = code
            # raise Exception(code)
            js.eval(code)

        self.registered = True


class Component:
    component_metadata: Metadata = None
    element: HTMLElement = None

    def __init_subclass__(cls, metadata: Metadata = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if metadata is None:
            metadata = Metadata(clazz=cls)
        cls.component_metadata = metadata
        if metadata.clazz is None:
            metadata.clazz = cls

        for name, value in cls.__dict__.items():
            if isinstance(value, attribute):
                cls.component_metadata.observed_attributes.add(name)

        if cls.component_metadata.auto_define:
            cls.component_metadata.define_element()

    def __init__(self, element_from_js=None):
        if element_from_js is None:
            self.element = js.eval(f'window.{self.component_metadata._js_class_name}').new(create_proxy(self))
        else:
            self.element = element_from_js

        self.init_component()

    def init_component(self):
        pass

    def connectedCallback(self):
        pass

    def disconnectedCallback(self):
        pass

    def adoptedCallback(self):
        pass

    def attributeChangedCallback(self, name: str, oldValue: str, newValue: str):
        pass

    def root_element(self):
        return self.element

    def find_element_field(self, name: str):
        root = self.root_element()
        selector = root.querySelector(f'[data-name="{name}"]')
        if selector is None:
            raise ElementNotFound(f'Not found data-name: [{name}] html: [{root.outerHTML}]')
        if hasattr(selector, '_py'):
            selector = selector._py
        self._check_type(name, selector)
        return selector

    def _check_type(self, name, selector):
        import inspect
        annotations = inspect.get_annotations(self.__class__)

        expected_type = annotations.get(name, None)
        if expected_type is None:
            # raise Exception(f'No type defined for field: {name}')
            return
        # raise Exception(f'type of expected_type: {type(expected_type)}')
        # test if expected_type is a class
        if not inspect.isclass(expected_type):
            return
        if not issubclass(expected_type, Component):
            return
        # raise Exception(f'Expected type: {expected_type} for field: {name} but found: {type(selector)}')
        isinst = not isinstance(selector, expected_type)
        # raise Exception(f'isinst: {isinst}')
        if isinst:
            raise WrongTypeDefinition(f'Expected type: {expected_type} for field: {name} but found: {type(selector)}')


class ElementNotFound(AttributeError): pass


class WrongTypeDefinition(TypeError): pass


# language=javascript
_custom_element_class_template = """
class $ClassName extends HTMLElement {
    static observedAttributes = [ $observedAttributes ];
    constructor(python_instance) {
        super();
        if (python_instance) 
            this._py = python_instance;
        else 
            this._py = $namespace.$ClassName(this);
    }

    connectedCallback()    { this._py.connectedCallback(); }
    disconnectedCallback() { this._py.disconnectedCallback(); }
    adoptedCallback()      { this._py.adoptedCallback(); }
    attributeChangedCallback(name, oldValue, newValue) { this._py.attributeChangedCallback(name, oldValue, newValue); }
}

customElements.define('$tagName', $ClassName);
window.$ClassName = $ClassName;
"""


class attribute:

    def __init__(self):
        self.name = None

    def __set_name__(self, owner, name):
        if not issubclass(owner, Component):
            raise Exception(f'attribute {name} must be in a subclass of {Component.__qualname__}')
        self.name = name

    def __get__(self, obj: Component, objtype=None):
        return obj.element.getAttribute(self.name)

    def __set__(self, obj: Component, value):
        obj.element.setAttribute(self.name, value)


class element:

    def __init__(self):
        self.name = None

    def __set_name__(self, owner, name):
        if not issubclass(owner, Component):
            raise Exception(f'attribute {name} must be in a subclass of {Component.__qualname__}')
        self.name = name

    def __get__(self, obj: Component, objtype=None):
        return obj.find_element_field(self.name)
