from __future__ import annotations

import js
from js import window, HTMLElement
from pyodide.ffi import create_proxy


class ComponentMetadata:
    def __init__(self, tag_name: str | None, clazz=None, auto_define=True):
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
        if self.auto_define:
            self.define_element()

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
    component_metadata: ComponentMetadata = None
    element: HTMLElement = None

    def __init_subclass__(cls):
        super().__init_subclass__()
        if cls.component_metadata is None:
            cls.component_metadata = ComponentMetadata(None, clazz=cls)
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


# language=javascript
_custom_element_class_template = """
class $ClassName extends HTMLElement {
    static observedAttributes = [ $observedAttributes ];
    constructor(python_instance) {
        super();
        //throw Exception('python_instance=' + python_instance);
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
