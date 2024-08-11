from __future__ import annotations

from datetime import timedelta

import pytest

from tests.server.filesystem_sync.activity_monitor import ActivityMonitor
from tests.server.filesystem_sync.time_mock import TimeMock

_time_mock = TimeMock()


@pytest.fixture
def target():
    _time_mock.reset()
    return ActivityMonitor(timedelta(milliseconds=20), time_func=_time_mock)


def test_activity_monitor(target):
    assert target.at_rest()


def test_touch__change_at_rest(target):
    target.touch()
    assert not target.at_rest()
    _time_mock.advance(timedelta(milliseconds=10))
    assert not target.at_rest()


def test_rest_delta(target):
    assert target.rest_delta() is None
    target.touch()
    _time_mock.advance(timedelta(milliseconds=10))
    assert target.rest_delta() == timedelta(milliseconds=10)


def test_touch_after_time_window(target):
    target.touch()
    _time_mock.advance(timedelta(milliseconds=21))
    assert target.at_rest()
