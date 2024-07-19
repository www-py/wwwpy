import ast

from dataclasses import dataclass
from typing import List


@dataclass
class AttrInfo:
    name: str
    type: str
    default: str

@dataclass
class ClassInfo:
    name: str
    attributes: List[AttrInfo]

@dataclass
class SourceInfo:
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
                attributes.append(AttrInfo(attr_name, attr_type, default))
        self.classes.append(ClassInfo(class_name, attributes))
        self.generic_visit(node)

def source_info(source):
    tree = ast.parse(source)
    extractor = ClassInfoExtractor()
    extractor.visit(tree)
    return SourceInfo(extractor.classes)