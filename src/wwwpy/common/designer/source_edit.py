import ast
from dataclasses import dataclass
from typing import List, Callable

import libcst as cst


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
                attr_type = self.get_annotation_type(item.annotation)
                default = ast.unparse(item.value) if item.value else None
                attributes.append(Attribute(attr_name, attr_type, default))
        self.classes.append(ClassInfo(class_name, attributes))
        self.generic_visit(node)

    def get_annotation_type(self, annotation):
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            names = []
            while isinstance(annotation, ast.Attribute):
                names.append(annotation.attr)
                annotation = annotation.value
            if isinstance(annotation, ast.Name):
                names.append(annotation.id)
            names.reverse()
            return '.'.join(names)
        else:
            return 'Unknown'


def info(source):
    tree = ast.parse(source)
    extractor = ClassInfoExtractor()
    extractor.visit(tree)
    return Info(extractor.classes)


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
            return updated_node.with_changes(
                body=updated_node.body.with_changes(body=list(updated_node.body.body) + [new_field_node]))
        return updated_node


def add_attribute(source_code: str, attr_info: Attribute):
    module = cst.parse_module(source_code)
    i = info(source_code)

    transformer = AddFieldToClassTransformer(i.classes[0].name, attr_info)
    modified_tree = module.visit(transformer)

    return modified_tree.code


def html_edit(source_code: str, html_manipulator: Callable[[str], str]) -> str:
    tree = cst.parse_module(source_code)
    transformer = HTMLStringUpdater(html_manipulator)
    modified_tree = tree.visit(transformer)
    return modified_tree.code


class HTMLStringUpdater(cst.CSTTransformer):
    def __init__(self, html_manipulator: Callable[[str], str]):
        super().__init__()
        self.html_manipulator = html_manipulator

    def leave_SimpleString(self, original_node: cst.SimpleString, updated_node: cst.SimpleString) -> cst.CSTNode:
        if original_node.value.startswith('"""') and original_node.value.endswith('"""'):
            original_html = original_node.value[3:-3]
            modified_html = self.html_manipulator(original_html)
            return updated_node.with_changes(value=f'"""{modified_html}"""')
        return updated_node


def add_component(source_code: str, attribute_name: str, attribute_type: str, html_piece: str) -> str:
    named_html = html_piece.replace('#name#', attribute_name)

    def manipulate_html(html):
        return html + named_html

    source1 = add_attribute(source_code, Attribute(attribute_name, attribute_type, 'wpc.element()'))
    source2 = html_edit(source1, manipulate_html)

    return source2
