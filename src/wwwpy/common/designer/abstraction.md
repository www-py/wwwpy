# Abstraction for editing a wwwpy.remote.component.Component


A ComponentLocator class has a:
- name, e.g., Component1
- filename, e.g.,  remote/component1.py
- some way to locate its html, e.g., a string constant inside the class or an external file like component1.html


## Definition of Component and Element:
- A Component defines and is coupled to its Custom Element (as in  html5 custom element)
- A Custom Element may not be tied to a Component

Component1 is a Component and as such defines also a Custom Element.
HTMLInputElement is an Element but it is not a Component


## Editing needs on an Element
### Affects both python and html:
- add
- rename (available when an element is selected)
- remove (available when an element is selected)

### Affects only the html (todo expand because it needs metadat)
- attributes, e.g., value='123'
- innerHTML
- move the element in the tree hierarchy
- slots?

### Affects only the python
- add or remove an event handler (available when an element is selected + an event associated to that element)


## Metadata needed for a Component class:
- list of attributes:
    - a data structure to represent the attribute,
      e.g., `input1: js.HTMLInputElement = wpc.element()`, or `component2: Component2 = wpc.element()`
      and the html part `<input data-name="input1">`
    - a way to locate its elements (code and html)
- list of methods with signature, e.g., input1__change
