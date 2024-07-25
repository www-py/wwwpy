import ast
from dataclasses import dataclass
from typing import List

import libcst as cst

from wwwpy.common.designer.source_info import Attribute, info
from wwwpy.common.designer.source_strings import html_string_edit


class AddFieldToClassTransformer(cst.CSTTransformer):
    def __init__(self, class_name, new_field: Attribute):
        super().__init__()
        self.class_name = class_name
        self.new_field = new_field

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            # Check if the type is a composite name (contains a dot)
            if '.' in self.new_field.type:
                base_name, attr_name = self.new_field.type.rsplit('.', 1)
                annotation = cst.Annotation(
                    cst.Attribute(
                        value=cst.Name(base_name),
                        attr=cst.Name(attr_name)
                    )
                )
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
            new_body = []
            inserted = False
            for item in updated_node.body.body:
                if not inserted and isinstance(item, cst.SimpleStatementLine) and isinstance(item.body[0],
                                                                                             cst.AnnAssign):
                    new_body.append(item)
                else:
                    if not inserted:
                        new_body.append(new_field_node)
                        inserted = True
                    new_body.append(item)

            if not inserted:
                new_body.append(new_field_node)

            return updated_node.with_changes(body=updated_node.body.with_changes(body=new_body))
        return updated_node


def add_attribute(source_code: str, attr_info: Attribute):
    module = cst.parse_module(source_code)
    i = info(source_code)

    transformer = AddFieldToClassTransformer(i.classes[0].name, attr_info)
    modified_tree = module.visit(transformer)

    return modified_tree.code


def add_component(source_code: str, attribute_name: str, attribute_type: str, html_piece: str) -> str:
    named_html = html_piece.replace('#name#', attribute_name)

    def manipulate_html(html):
        return html + named_html

    source1 = add_attribute(source_code, Attribute(attribute_name, attribute_type, 'wpc.element()'))
    source2 = html_string_edit(source1, manipulate_html)

    return source2
