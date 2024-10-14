from dataclasses import dataclass
from typing import List, Dict

import wwwpy.remote.component as wpc
import js

import logging

from wwwpy.remote import dict_to_js

logger = logging.getLogger(__name__)


@dataclass
class Item:
    title: str
    description: str
    values: Dict = None


class SearchableList1(wpc.Component, tag_name='wwwpy-searchable-list-1'):
    _container: js.HTMLDivElement = wpc.element()
    _search_box: js.HTMLInputElement = wpc.element()
    _no_results: js.HTMLDivElement = wpc.element()
    _info: js.HTMLElement = wpc.element()
    _items: List[Item] = []

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div style='padding: 0.5em'>
    <input type='search' data-name="_search_box" placeholder='Search...'>
    <span data-name="_info"></span>
    <hr>        
    <div data-name="_no_results"></div>
    <div data-name="_container"></div>
</div>      
"""
        self.items = [Item(f'title {i}', f'description {i}') for i in range(3)]

    @property
    def placeholder(self) -> str:
        return self._search_box.placeholder

    @placeholder.setter
    def placeholder(self, value):
        self._search_box.placeholder = value

    @property
    def items(self) -> List[Item]:
        return self._items

    @items.setter
    def items(self, value: List[Item]):
        self._items = value
        self._container.innerHTML = ''
        for item in value:
            row = Component3()
            row.item = item
            row.title.innerHTML = item.title
            row.description.innerHTML = item.description
            row.element.style.padding = '0.1em'  # I don't know what this does
            self._container.append(row.element)
        self._update_search()

    def _update_search(self):
        search_value = self._search_box.value.lower()
        visible = 0
        for ele in self._container.children:
            comp: Component3 = wpc.get_component(ele)
            if not comp:
                continue
            show = search_value in comp.search_text.lower()
            if show:
                visible += 1
            ele.style.display = '' if show else 'none'

        self._no_results.innerHTML = 'No results' if visible == 0 else ''
        item_word = 'item' if visible == 1 else 'items'
        self._info.innerText = f'Showing {visible} of {len(self._items)} {item_word}'

    async def _search_box__input(self, event):
        js.console.log('handler _search_box__input event =', event)
        self._update_search()


class Component3(wpc.Component):
    title: js.HTMLDivElement = wpc.element()
    description: js.HTMLDivElement = wpc.element()
    item: Item

    @property
    def search_text(self) -> str:
        return self.title.innerText + ' ' + self.description.innerText

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<style>
.row-highlight:hover {
    background-color: DimGray;    
}
.row-highlight {
    cursor: pointer;
}
</style>        
<div class='row-highlight' data-name="_row">
    <div data-name="title" style='font-weight: bold ; margin-bottom: 0.4em'>Title</div>
    <div data-name="description">Description</div>
</div>
        """
        self.item: Item = None

    def _row__click(self, event: js.MouseEvent):
        event.stopPropagation()
        event.preventDefault()
        new = js.CustomEvent.new('item-click', dict_to_js({'detail': self.item, 'bubbles': True}))
        self.element.dispatchEvent(new)
