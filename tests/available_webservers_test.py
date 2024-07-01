from collections.abc import Iterator

from wwwpy.webservers.available_webservers import available_webservers


def test_at_least_one():
    next(available_webservers().ids)


def test_ids():
    for ws_id in available_webservers().ids:
        assert isinstance(ws_id, str)
        assert ws_id.isidentifier()


def test_new_instance():
    instance = available_webservers().new_instance()
    assert instance is not None


def test_instances():
    instances = available_webservers().instances()
    assert isinstance(instances, Iterator)
