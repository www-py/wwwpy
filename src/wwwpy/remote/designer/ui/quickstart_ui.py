from wwwpy.common.quickstart import quickstart_list
from wwwpy.remote.designer.ui.draggable_component import new_window, WindowResult
from wwwpy.remote.designer.ui.searchable_list_1 import SearchableList1, Item
import js
from pyodide.ffi import create_proxy


def show_selector():
    dg = new_window("Select a quickstart", closable=False)
    dg.window.set_size('300px', '300px')
    dg.window.set_position('40','40')
    cmp1 = SearchableList1()
    cmp1.items = [Item(qs.title, qs.description, {'quickstart': qs}) for qs in quickstart_list()]
    cmp1.placeholder = 'Search or select below...'
    dg.element.append(cmp1.element)
    js.document.body.append(dg.element)

    def item_click(event):
        item = event.detail
        dg.element.remove()

    cmp1.element.addEventListener('item-click', create_proxy(item_click))
