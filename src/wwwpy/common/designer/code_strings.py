from typing import Callable

import libcst as cst


def html_string_edit(source_code: str, class_name: str, html_manipulator: Callable[[str], str]) -> str:
    """This function modifies the HTML string in the source code using the provided manipulator function.
    It only modifies the HTML string within the specified class.
    """
    tree = cst.parse_module(source_code)
    transformer = HTMLStringUpdater(class_name, html_manipulator)
    modified_tree = tree.visit(transformer)
    return modified_tree.code


class HTMLStringUpdater(cst.CSTTransformer):
    def __init__(self, class_name: str, html_manipulator: Callable[[str], str]):
        super().__init__()
        self.class_name = class_name
        self.html_manipulator = html_manipulator
        self.current_class = None

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self.current_class = node.name.value

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.CSTNode:
        self.current_class = None
        return updated_node

    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString) -> cst.CSTNode:
        if self.current_class == self.class_name and original_node.value.startswith('"""') and original_node.value.endswith('"""'):
            original_html = original_node.value[3:-3]
            modified_html = self.html_manipulator(original_html)
            return updated_node.with_changes(value=f'"""{modified_html}"""')
        return updated_node