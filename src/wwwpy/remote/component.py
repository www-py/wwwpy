from __future__ import annotations

import js
from js import window, HTMLElement
from pyodide.ffi import create_proxy


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
        js_class_name = self.clazz.__name__
        self._js_class_name = js_class_name
        setattr(window, f'python_constructor_{js_class_name}', self.clazz)

        obs_attr = ', '.join(f'"{attr}"' for attr in self.observed_attributes)
        code = (_custom_element_class_template
                .replace('$ClassName', js_class_name)
                .replace('$tagName', self.tag_name)
                .replace('$observedAttributes', obs_attr)
                )
        self._custom_element_class_template = code
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

    def find_element(self, name: str):
        selector = self.element.querySelector(f'[name="{name}"]')
        if selector is None:
            raise ElementNotFound(f'Name: [{name}] html: [{self.element.outerHTML}]')
        return selector


class ElementNotFound(AttributeError): pass


# language=javascript
_custom_element_class_template = """
class $ClassName extends HTMLElement {
    static observedAttributes = [ $observedAttributes ];
    constructor(python_instance) {
        super();
        if (python_instance) 
            this._py = python_instance;
        else 
            this._py = window.python_constructor_$ClassName(this);
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
        target = obj.find_element(self.name)
        if hasattr(target, '_py'):
            return target._py
        return target
