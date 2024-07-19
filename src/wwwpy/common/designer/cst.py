from dataclasses import dataclass
from typing import List

import libcst as cst
import libcst

class AddFieldToClassTransformer(cst.CSTTransformer):
    def __init__(self, class_name, new_field):
        super().__init__()
        self.class_name = class_name
        self.new_field = new_field

    def leave_ClassDef(self, original_node, updated_node):
        if original_node.name.value == self.class_name:
            new_field_node = cst.SimpleStatementLine([
                cst.AnnAssign(
                    target=cst.Name(self.new_field['name']),
                    annotation=cst.Annotation(cst.Name(self.new_field['type'])),
                    value=cst.Integer(self.new_field['default'])  # Changed from cst.Name to cst.Integer
                )
            ])
            return updated_node.with_changes(
                body=updated_node.body.with_changes(body=[new_field_node] + list(updated_node.body.body)))
        return updated_node


def main():
    # Define the new field you want to add
    new_field = {
        'name': 'new_field',
        'type': 'int',
        'default': '0'
    }

    # Parse the source code
    source_code = """
class MyClass:
    ...
    """

    module = cst.parse_module(source_code)
    transformer = AddFieldToClassTransformer("MyClass", new_field)
    modified_tree = module.visit(transformer)

    # Print the modified code
    print(modified_tree.code)


if __name__ == "__main__":
    main()


@dataclass()
class AttrInfo:
    name: str
    type: str
    default: str


@dataclass()
class ClassInfo:
    name: str
    attributes: List[AttrInfo]


@dataclass()
class SourceInfo:
    classes: List[ClassInfo]

import libcst as cst

class ClassInfoExtractor(cst.CSTVisitor):
    def __init__(self):
        super().__init__()
        self.classes = []

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        class_name = node.name.value
        attributes = []

        for element in node.body.body:
            if isinstance(element, cst.SimpleStatementLine):
                for item in element.body:
                    if isinstance(item, cst.AnnAssign):
                        attr_name = item.target.value
                        attr_type = item.annotation.annotation.value
                        # Default value handling is simplified; real scenarios may need more complex logic
                        default = libcst.Module([]).code_for_node(item.value)
                        attributes.append(AttrInfo(name=attr_name, type=attr_type, default=default))

        self.classes.append(ClassInfo(name=class_name, attributes=attributes))

def source_info(source: str) -> SourceInfo:
    module = cst.parse_module(source)
    extractor = ClassInfoExtractor()
    module.visit(extractor)

    return SourceInfo(classes=extractor.classes)