from pathlib import Path

from wwwpy.common.designer.code_finder import find_source_file


def test_find_component__should_be_this_very_same_file():
    class SomeClass:
        pass

    path = find_source_file(SomeClass)
    assert path == Path(__file__).resolve()
