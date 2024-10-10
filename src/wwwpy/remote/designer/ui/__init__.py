def show_explorer():
    from wwwpy.remote.designer.ui.filesystem_tree import FilesystemTree
    from wwwpy.remote.designer.ui.filesystem_tree import DraggableComponent

    from js import document
    import js
    # language=html
    component = DraggableComponent()

    fragment = js.document.createRange().createContextualFragment(f"""
            <span slot='title'>Browse local filesystem <button data-name="close" style="cursor:pointer">X</button></span>
            <div data-name="pre1"></div>
            """)
    selector = fragment.querySelector(f'[data-name="close"]')
    selector.onclick = lambda ev: component.element.remove()
    pre1: js.HTMLElement = fragment.querySelector(f'[data-name="pre1"]')
    tree = FilesystemTree()
    tree.show_path('/')
    pre1.append(tree.element)
    component.element.append(fragment)

    js.document.body.append(component.element)
