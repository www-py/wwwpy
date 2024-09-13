from __future__ import annotations

from dataclasses import dataclass

import libcst as cst

from wwwpy.common.designer import code_info
from wwwpy.common.designer.code_info import Attribute, info
from wwwpy.common.designer.code_strings import html_string_edit
from wwwpy.common.designer.html_edit import Position, html_add
from wwwpy.common.designer.html_locator import NodePath


def add_attribute(source_code: str, class_name: str, attr_info: Attribute):
    module = cst.parse_module(source_code)
    transformer = _AddFieldToClassTransformer(class_name, attr_info)
    modified_tree = module.visit(transformer)

    return modified_tree.code


@dataclass
class ComponentDef:
    base_name: str
    attribute_type: str
    html_piece: str


# def add_component(source_code: str, attr_name: str, attribute_type: str, html_piece: str, position: Position) -> str:
#     named_html = html_piece.replace('#name#', attr_name)
#
#     def manipulate_html(html):
#         return html + named_html
#
#     source1 = add_attribute(source_code, Attribute(attr_name, attribute_type, 'wpc.element()'))
#     source2 = html_string_edit(source1, manipulate_html)
#
#     return source2

def add_component(source_code: str, class_name: str, comp_def: ComponentDef, node_path: NodePath,
                  position: Position) -> str | None:
    classes = code_info.info(source_code).classes
    filtered_classes = [clazz for clazz in classes if clazz.name == class_name]
    if len(filtered_classes) == 0:
        print(f'Class {class_name} not found inside source ```{source_code}```')
        return None

    class_info = filtered_classes[0]
    attr_name = class_info.next_attribute_name(comp_def.base_name)
    named_html = comp_def.html_piece.replace('#name#', attr_name)

    source1 = add_attribute(source_code, class_name, Attribute(attr_name, comp_def.attribute_type, 'wpc.element()'))

    def manipulate_html(html):
        add = html_add(html, named_html, node_path, position)
        return add

    source2 = html_string_edit(source1, class_name, manipulate_html)

    return source2


class _AddFieldToClassTransformer(cst.CSTTransformer):
    def __init__(self, class_name, new_field: Attribute):
        super().__init__()
        self.class_name = class_name
        self.new_field = new_field

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value != self.class_name:
            return original_node
        # Check if the type is a composite name (contains a dot)
        if '.' in self.new_field.type:
            base_name, attr_name = self.new_field.type.rsplit('.', 1)
            annotation = cst.Annotation(cst.Attribute(value=cst.Name(base_name), attr=cst.Name(attr_name)))
        else:
            annotation = cst.Annotation(cst.Name(self.new_field.type))

        new_field_node = cst.SimpleStatementLine([
            cst.AnnAssign(
                target=cst.Name(self.new_field.name),
                annotation=annotation,
                value=None if self.new_field.default is None else cst.parse_expression(self.new_field.default)
            )
        ])

        # Find the position to insert the new attribute
        last_assign_index = 0
        for i, item in enumerate(updated_node.body.body):
            if isinstance(item, cst.SimpleStatementLine) and isinstance(item.body[0], cst.AnnAssign):
                last_assign_index = i + 1

        new_body = list(updated_node.body.body)
        new_body.insert(last_assign_index, new_field_node)

        return updated_node.with_changes(body=updated_node.body.with_changes(body=new_body))


def add_method(source_code: str, class_name: str, method_name: str, method_args: str) -> str:
    # todo
    return 'todo'
