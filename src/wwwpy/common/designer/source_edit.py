import ast

from dataclasses import dataclass
from typing import List


@dataclass
class Attribute:
    name: str
    type: str
    default: str


@dataclass
class ClassInfo:
    name: str
    attributes: List[Attribute]


@dataclass
class Info:
    classes: List[ClassInfo]


class ClassInfoExtractor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        class_name = node.name
        attributes = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                attr_name = item.target.id
                attr_type = item.annotation.id
                default = ast.unparse(item.value) if item.value else None
                attributes.append(Attribute(attr_name, attr_type, default))
        self.classes.append(ClassInfo(class_name, attributes))
        self.generic_visit(node)


def info(source):
    tree = ast.parse(source)
    extractor = ClassInfoExtractor()
    extractor.visit(tree)
    return Info(extractor.classes)


import ast

import libcst as cst
import libcst


class AddFieldToClassTransformer(cst.CSTTransformer):
    def __init__(self, class_name, new_field: Attribute):
        super().__init__()
        self.class_name = class_name
        self.new_field = new_field

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            new_field_node = cst.SimpleStatementLine([
                cst.AnnAssign(
                    target=cst.Name(self.new_field.name),
                    annotation=cst.Annotation(cst.Name(self.new_field.type)),
                    value=None if self.new_field.default is None else cst.parse_expression(self.new_field.default)
                )
            ])
            return updated_node.with_changes(
                body=updated_node.body.with_changes(body=list(updated_node.body.body) + [new_field_node]))
        return updated_node


def add_attribute(source_code: str, attr_info: Attribute):
    module = cst.parse_module(source_code)
    i = info(source_code)

    transformer = AddFieldToClassTransformer(i.classes[0].name, attr_info)
    modified_tree = module.visit(transformer)

    return modified_tree.code
