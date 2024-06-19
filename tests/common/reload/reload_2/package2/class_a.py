print('loading ClassA... 123')
import package2.class_b as class_b


class ClassA:
    def __init__(self):
        self.b = 45
        self.class_b = class_b.ClassB()
