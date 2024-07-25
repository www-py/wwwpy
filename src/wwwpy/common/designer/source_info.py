import ast
from dataclasses import dataclass
from typing import List


def info(python_source: str) -> 'Info':
    tree = ast.parse(python_source)
    extractor = _ClassInfoExtractor()
    extractor.visit(tree)
    return Info(extractor.classes)


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


class _ClassInfoExtractor(ast.NodeVisitor):
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
