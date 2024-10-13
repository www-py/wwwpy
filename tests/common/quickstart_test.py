from wwwpy.common.quickstart import quickstart_list, is_empty_project


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


def test_empty_project(tmp_path):
    assert is_empty_project(tmp_path)


def test_empty_project2(tmp_path):
    (tmp_path / 'remote').mkdir()
    (tmp_path / '__pycache__').mkdir()
    assert is_empty_project(tmp_path)


def test_empty_project3(tmp_path):
    (tmp_path / 'remote').mkdir()
    (tmp_path / 'remote/__init__.py').touch()
    assert is_empty_project(tmp_path)


def test_not_empty_project(tmp_path):
    remote = tmp_path / 'remote'
    remote.mkdir()
    (remote / '__init__.py').write_text('# some content')
    assert not is_empty_project(tmp_path)


def test_not_empty_project2(tmp_path):
    (tmp_path / 'some-file.txt').touch()
    assert not is_empty_project(tmp_path)
