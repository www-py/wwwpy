import pytest

from wwwpy.server.filesystem_sync import Event


def test_strip_container():
    # GIVEN
    event = Event('created', False, '/tmp/folder1/source/dir1/file1.txt', '/tmp/folder1/source/dir2/file1.txt')

    # WHEN
    actual = event.strip_container('/tmp/folder1/source')

    # THEN
    expect = Event('created', False, '/dir1/file1.txt', '/dir2/file1.txt')
    assert actual == expect


def test_strip_container__with_dest_empty__shouldNotFail():
    event = Event('created', False, '/tmp/folder1/source/dir1/file1.txt', '')

    actual = event.strip_container('/tmp/folder1/source')

    expect = Event('created', False, '/dir1/file1.txt', '')
    assert actual == expect


def test_strip_container__with_dest_notContained__shouldFail():
    event = Event('created', False, '/tmp/folder1/source/dir1/file1.txt', '/tmp/folder1/other/dir2/file1.txt')

    with pytest.raises(ValueError):
        event.strip_container('/tmp/folder1/source')


def test_strip_container__shouldRaiseIf_pathsAreNot_containedInPath():
    event = Event('created', False, '/tmp/folder1/source/dir1/file1.txt', '/tmp/folder1/source/dir2/file1.txt')

    with pytest.raises(ValueError):
        event.strip_container('/tmp/folder1/other')


def test_against_a_simple_replace_in_implementation():
    # GIVEN
    event = Event('created', False, '/source/source/dir1/file1.txt', '/source/dir2/file1.txt')

    # WHEN
    actual = event.strip_container('/source')

    # THEN
    expect = Event('created', False, '/source/dir1/file1.txt', '/dir2/file1.txt')
    assert actual == expect


def test_strip_entire_path__shouldNotReturnEmptyString_but_slash():
    # GIVEN
    event = Event('created', False, '/source')

    # WHEN
    actual = event.strip_container('/source')

    # THEN
    expect = Event('created', False, '/', '')
    assert actual == expect

def test_strip_entire_path__dest__shouldNotReturnEmptyString_but_slash():
    # GIVEN
    event = Event('created', False, '/source', '/source')

    # WHEN
    actual = event.strip_container('/source')

    # THEN
    expect = Event('created', False, '/', '/')
    assert actual == expect
