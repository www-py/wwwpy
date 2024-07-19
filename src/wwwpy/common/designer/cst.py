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


import ast

def source_add_attribute(source, attr_info):
    class AddAttributeTransformer(ast.NodeTransformer):
        def visit_ClassDef(self, node):
            # Check if this is the target class by name
            if node.name == "MyElement":
                # Create a new AnnAssign node for the new attribute
                new_attr = ast.AnnAssign(
                    target=ast.Name(id=attr_info.name, ctx=ast.Store()),
                    annotation=ast.Name(id=attr_info.type, ctx=ast.Load()),
                    value=ast.Call(
                        func=ast.Name(id=attr_info.default.split('(')[0], ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    ),
                    simple=1
                )
                # Append the new attribute to the end of the class body
                node.body.append(new_attr)
            return node

    # Parse the source code into an AST
    tree = ast.parse(source)
    # Transform the AST
    transformer = AddAttributeTransformer()
    transformed_tree = transformer.visit(tree)
    # Unparse the AST back into source code
    new_source = ast.unparse(transformed_tree)
    return new_source