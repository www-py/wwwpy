from datetime import timedelta

import pytest

from tests.server.filesystem_sync.time_mock import TimeMock
from wwwpy.server.filesystem_sync.debouncer import Debouncer


class DebounceFixture:

    def __init__(self):
        self.wakeup_count = 0
        self.time_mock = TimeMock()
        self.target = Debouncer(timedelta(milliseconds=100), self._wakeup, self.time_mock)

    def _wakeup(self, debouncer):
        assert debouncer is self.target
        self.wakeup_count += 1


@pytest.fixture
def deb():
    return DebounceFixture()


def test_no_event(deb):
    # GIVEN

    # WHEN
    events = deb.target.events()
    delta = deb.target.time_until_next_emission()

    # THEN
    assert events == []
    assert deb.wakeup_count == 0
    assert delta is deb.target.window


def test_single_event__should_wakeup(deb):
    # GIVEN

    # WHEN
    deb.target.add_event("event1")

    # THEN
    assert deb.wakeup_count == 1
    assert deb.target.time_until_next_emission() == timedelta(milliseconds=100)


def test_two_events__should_wakeup_only_once(deb):
    # GIVEN

    # WHEN
    deb.target.add_event("event1")
    deb.target.add_event("event2")

    # THEN
    assert deb.wakeup_count == 1
    assert deb.target.time_until_next_emission() == timedelta(milliseconds=100)


def test_single_event(deb):
    # GIVEN
    deb.target.add_event("event1")

    # WHEN
    events = deb.target.events()

    # THEN
    assert events == []


def test_single_event__after_timeout(deb):
    # GIVEN
    deb.target.add_event("event1")
    deb.time_mock.advance(timedelta(milliseconds=101))

    # WHEN
    events = deb.target.events()

    # THEN
    assert events == ["event1"]
    assert deb.wakeup_count == 1
    assert deb.target.time_until_next_emission() == deb.target.window


def test_two_debounce__and_no_timeout(deb):
    # GIVEN
    deb.target.add_event("event1")
    deb.target.add_event("event2")

    # WHEN
    events = deb.target.events()

    # THEN
    assert events == []
    assert deb.wakeup_count == 1
    assert deb.target.time_until_next_emission() == timedelta(milliseconds=100)


def test_time_until(deb):
    # GIVEN
    deb.target.add_event("event1")
    deb.target.add_event("event2")
    deb.time_mock.advance(timedelta(milliseconds=101))

    # WHEN
    delta = deb.target.time_until_next_emission()

    # THEN
    assert delta == timedelta(milliseconds=-1)
    assert deb.wakeup_count == 1


def test_two_debounce__and_timeout(deb):
    # GIVEN
    for i in range(10):
        deb.target.add_event(f"e{i}")
        deb.time_mock.advance(timedelta(milliseconds=10))

    # WHEN
    events = deb.target.events()

    # THEN
    assert events == []
    assert deb.wakeup_count == 1
    assert deb.target.time_until_next_emission() == timedelta(milliseconds=90)


def test_two_debounce_and_timeout__should_return_to_one_wakeup_on_new_event(deb):
    # GIVEN
    deb.target.add_event("event1")
    deb.target.add_event("event2")
    deb.time_mock.advance(timedelta(milliseconds=101))
    deb.target.events()  # consume the events

    # WHEN
    deb.target.add_event("event3")

    # THEN
    assert deb.wakeup_count == 2

    # WHEN
    deb.time_mock.advance(timedelta(milliseconds=101))
    events = deb.target.events()

    # THEN
    assert events == ["event3"]
    assert deb.wakeup_count == 2


def test_is_debouncing__no_event(deb):
    # GIVEN

    # WHEN
    result = deb.target.is_debouncing

    # THEN
    assert not result


def test_is_debouncing__single_event(deb):
    # GIVEN
    deb.target.add_event("event1")

    # WHEN
    result = deb.target.is_debouncing

    # THEN
    assert result


def test_is_debouncing__single_event__after_timeout(deb):
    # GIVEN
    deb.target.add_event("event1")
    deb.time_mock.advance(timedelta(milliseconds=101))
    deb.target.events()  # this is required because we intend is_debouncing up until the events are consumed

    # WHEN
    result = deb.target.is_debouncing

    # THEN
    assert not result
