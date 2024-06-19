print('loading ClassA... 123')
from tests.common.reload.reload_2.class_b import ClassB


class ClassA:
    def __init__(self):
        self.a = 123
        self.class_b = ClassB()
