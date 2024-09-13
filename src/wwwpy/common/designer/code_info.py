import ast
import sys
from dataclasses import dataclass, field
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
class Method:
    name: str
    def_lineno: int
    code_lineno: int


@dataclass
class ClassInfo:
    name: str
    attributes: List[Attribute]
    methods: List[Method] = field(default_factory=list)

    def next_attribute_name(self, base_name):
        used = set([attr.name for attr in self.attributes])
        for i in range(1, sys.maxsize):
            name = f'{base_name}{i}'
            if name not in used:
                return name
        raise ValueError('Really?')


@dataclass
class Info:
    classes: List[ClassInfo]


class _ClassInfoExtractor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        class_name = node.name
        attributes = []
        methods = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                attr_name = item.target.id
                attr_type = self.get_annotation_type(item.annotation)
                default = ast.unparse(item.value) if item.value else None
                attributes.append(Attribute(attr_name, attr_type, default))
            elif isinstance(item, ast.FunctionDef):
                methods.append(Method(item.name, item.lineno, item.body[0].lineno))
        self.classes.append(ClassInfo(class_name, attributes, methods))
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
