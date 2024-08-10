# Abstraction for editing a wwwpy.remote.component.Component

## Definition of Component and Element:
- A Component is an Element (as in  html5 custom element)
- Not all Elements are Components.
Component1 is a Component and as such also an Element
HTMLInputElement is an Element but it is not a Component


## Editing needs on an Element
### Affects both python and html:
- add
- rename
- remove

### Affects only the html
- attributes, e.g., value='123'
- innerHTML
- move the element in the tree hierarchy
- slots?

### Affects only the python
- add or remove an event handler


## A Component class has a:
- name, e.g., Component1
- filename, e.g.,  remote/component1.py
- some way to locate its html, e.g., a string constant inside the class or an external file like component1.html


## Metadata needed for a Component class:
- list of attributes:
    - a data structure to represent the attribute,
      e.g., `input1: js.HTMLInputElement = wpc.element()`, or `component2: Component2 = wpc.element()`
      and the html part `<input data-name="input1">`
    - a way to locate its elements (code and html)
- list of methods with signature, e.g., input1__change
