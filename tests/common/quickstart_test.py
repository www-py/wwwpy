from wwwpy.common.quickstart import quickstart_list


def test_quickstart_list():
    target = quickstart_list()
    assert target is not None
    assert len(target) > 0


def test_basic():
    target = quickstart_list()
    basic = target.get('basic')
    assert basic is not None
    assert basic.name == 'basic'
    assert basic.title == 'Basic setup for a new project'
    assert basic.description == 'It contains just a simple Component with almost no content'

def test_basic_should_be_the_first():
    target = quickstart_list()
    first = target[0]
    assert first.name == 'basic'
