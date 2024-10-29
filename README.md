<h1>Hey there! wwwpy has moved! You can now find it at https://github.com/wwwpy-labs/wwwpy</h1>

# wwwpy

[python_versions]: https://img.shields.io/pypi/pyversions/wwwpy.svg?logo=python&logoColor=white

[![Test suite](https://github.com/www-py/wwwpy/actions/workflows/ci.yml/badge.svg)](https://github.com/www-py/wwwpy/actions/workflows/ci.yml)
![PyPI](https://img.shields.io/pypi/v/wwwpy)
[![Python Versions][python_versions]](https://pypi.org/project/wwwpy/)


Develop web applications in Python quickly and easily.

The vision of wwwpy: 
- **Jumpstart Your Projects**: With just a couple of commands, get a head start on building web UIs, allowing you to focus on coding and scaling your application.
- **Build Web UIs**: Create web interfaces without the need to focus on the frontend. Everything is Python. You can avoid HTML/DOM/CSS/JavasScript, but you can use the full power of it, if you want. Use the drag-and-drop UI builder for rapid prototyping, while still being able to easily create, extend, and customize UIs as needed.
- **Integrated Development Environment**: use an intuitive UI building experience within the development environment, making it easy to edit properties and components as you go.
- **Direct Code Integration**: UI components are fully reflected in the source code, allowing for manual edits. Every change is versionable and seamlessly integrates with your source code repository.
- **Hot reload**: When in dev-mode, any change to the source code is immediately reflected in the running application.
- **Client-server**: Call server-side functions from the browser seamlessly, without the need to write api endpoints. Oh, you also can call the browser(s) from the server to push changes and information to it.
- **Versatile Scalability**: From quick UI prototypes to large-scale enterprise applications, wwwpy handles everything from simple interfaces to complex projects with external dependencies and integrations.

# How to Use

### Installation

```
pip install wwwpy
```

### Getting Started
To start developing:

```
wwwpy dev
```

If the current folder is empty, wwwpy will ask you to select a quickstart project to help you explore its features right away.


## Documentation

* [Introduction](docs/introduction.md): Learn about the project structure and how to get started.
* [Component Documentation](docs/component.md): Instructions on how to use and create components.
* [Seamless communication between server and browser(s)](docs/rpc.md): Learn about seamless communication between the server and browser(s).

## Roadmap
Our primary focus is to get to know how you are using wwwpy and what are the problems you are solving now or trying to solve. 
Please, reach out to us and share your experience.

Disclaimer: This roadmap is fluid and we will change according to your feedback. If you have comments or ideas, please open an issue or post a message in a discussion.

- Add support for [Plotly](https://plotly.com/javascript/)
- Add support for [AG Grid](https://ag-grid.com) 
- Add support for Ionic custom web components
  Add support for ASGI. This will enable wwwpy to be used as an add-on to e.g., Django
- Create a database quickstart with vanilla SQLite (or SQLAlchemy)
- Documentation and tutorial about keybindings (hotkey and shortcuts)
- PyCharm and VS Code plugin
- Implement a simple layout system to easily place components
- Execute/Schedule server-side code [see issue](https://github.com/www-py/wwwpy/issues/7)
- Support IDE Python completion for shoelace property (through Python stubs .pyi)
- Support server.rpc function signature hot-reload (now if you change the parameters of a function, the hot-reload will not pick it up)
- Improve the serialization mechanism of RPC
- Change the default event handler code from 'console.log' to 'logger.debug' to use the Python API. As a side effect, all the logging is sent to the server console (only in dev-mode)
- Improve and clean the Component API that handle the shadow DOM
- Add a cute loader instead of the plain `<h1>Loading...</h1>`


### Toolbox improvements:
- Improve the selection mechanism; it should be smarter and 'do the right thing' given the context
- Implement the deletion of an element
- Give better visibility to "Create new Component" and "Explore local filesystem"; now they are at the bottom of the item list
- Develop a 'manual' element selection for those element not easily selected with the mouse
- Implement the rename of an element
- Dynamically include the user custom Components in the palette so they can be dropped and used
- When creating event handlers, add type hints to the event parameter, e.g., `def button1__click(self, event: js.MouseEvent)`
- Setting the data-name should declare the Python definition
- Removing the data-name should remove the Python definition
- Improve the editing of third-party components (e.g., shoelace). Some components have constraints on parents or children, facilitate that (also standard elements have constraints like this).


