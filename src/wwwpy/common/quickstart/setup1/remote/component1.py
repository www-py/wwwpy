import wwwpy.remote.component as wpc
import js


class Component1(wpc.Component, tag_name='component-1'):

    def init_component(self):
        # language=html
        self.element.innerHTML = """<span>component-1</span>"""
