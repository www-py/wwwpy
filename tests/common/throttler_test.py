from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from wwwpy.common.throttler import EventThrottler, Event


class TimeMock:
    def __init__(self):
        self.now = datetime(2021, 1, 1, 0, 0, 0, 0)

    def time(self):
        return self.now

    def add(self, delta):
        self.now = self.now + delta


class EventRecorder:
    def __init__(self):
        self.list = []

    def append(self, event):
        self.list.append(event)

    def clear(self):
        self.list.clear()


class ThrottlerFixture:

    def __init__(self):
        self.wakeup_requests = []
        self.events = EventRecorder()
        self.time = TimeMock()
        self.target = EventThrottler(50, self.events.append, self.time.time)
        self.target.wakeup = self._wakeup

    def _wakeup(self):
        self.wakeup_requests.append(None)

    def wakeup_count(self):
        return len(self.wakeup_requests)


@pytest.fixture
def throttler():
    return ThrottlerFixture()


def test_event_manager(throttler):
    e1 = Event('a', 'create')
    throttler.target.new_event(e1)
    assert throttler.wakeup_count() == 1
    assert throttler.events.list == []  # emit are done in the thread
    throttler.target.process_queue()
    assert throttler.events.list == [e1]


def test_event_in_window_should_be_withhold(throttler):
    throttler.target.new_event(Event('a', 'create'))
    throttler.events.clear()

    throttler.time.add(timedelta(milliseconds=40))

    e2 = Event('a', 'modify')
    throttler.target.new_event(e2)
    assert throttler.events.list == []


def test_next_action_time(throttler):
    assert throttler.target.next_action_delta() is None
    throttler.target.new_event(Event('a', 'create'))
    assert throttler.target.next_action_delta() == timedelta(milliseconds=0)
    throttler.target.process_queue()  # emit the initial event
    assert throttler.target.next_action_delta() == timedelta(milliseconds=50)


def test_emit_after_throttling(throttler):
    throttler.target.new_event(Event('a', 'create'))
    throttler.target.process_queue()

    throttler.time.add(timedelta(milliseconds=40))

    e2 = Event('a', 'modify')
    throttler.target.new_event(e2)

    throttler.time.add(timedelta(milliseconds=11))

    throttler.events.list.clear()
    throttler.target.process_queue()
    assert throttler.events.list == [e2]


def test_emit_after_discarding_one_event(throttler):
    throttler.target.new_event(Event('a', 'create'))
    throttler.target.process_queue()

    throttler.events.list.clear()

    throttler.time.add(timedelta(milliseconds=40))

    throttler.target.new_event(Event('a', 'modify'))  # will be discarded

    throttler.time.add(timedelta(milliseconds=5))

    ev = Event('a', 'modify2')
    throttler.target.new_event(ev)
    throttler.target.process_queue()
    assert throttler.events.list == []  # because we are still in the throttling window

    throttler.time.add(timedelta(milliseconds=6))
    throttler.target.process_queue()
    assert throttler.events.list == [ev]


def test_wakeup(throttler):
    assert throttler.wakeup_count() == 0
    throttler.target.new_event(Event('a', 'create'))
    assert throttler.wakeup_count() == 1


def test_eviction_fast(throttler):
    # if the thread is not fast enough we could lose the first event
    throttler.target.new_event(Event('a', 'create'))
    throttler.target.process_queue()

    throttler.time.add(timedelta(milliseconds=60))
    throttler.target.process_queue()

    assert throttler.target.next_action_delta() is None


def test_eviction_slow(throttler):
    # if the thread is not fast enough we could lose the first event
    throttler.target.new_event(Event('a', 'create'))
    throttler.time.add(timedelta(milliseconds=60))
    throttler.target.process_queue()

    assert throttler.target.next_action_delta() is None


def test_two_throttling_events_on_the_same_key(throttler):
    throttler.target.new_event(Event('a', 'create'))
    throttler.time.add(timedelta(milliseconds=40))
    throttler.target.new_event(Event('a', 'modify'))
    throttler.time.add(timedelta(milliseconds=11))
    throttler.target.process_queue()
    throttler.events.clear()

    throttler.time.add(timedelta(milliseconds=9))
    event = Event('a', 'modify2')
    throttler.target.new_event(event)  # this should be emitted immediately
    throttler.target.process_queue()
    assert throttler.events.list == [event]


def test_eviction_when_event_dies_in_throttled_state(throttler):
    throttler.target.new_event(Event('a', 'create'))
    throttler.target.process_queue()  # the FIRST is emitted and the state is changed to THROTTLE

    throttler.time.add(timedelta(milliseconds=60))
    throttler.target.process_queue()  # the THROTTLE should be evicted

    assert throttler.target.next_action_delta() is None

    # to be sure it was evicted, we send another event that should be immediately emitted
    throttler.events.clear()
    event = Event('a', 'modify')
    throttler.target.new_event(event)
    throttler.target.process_queue()

    assert throttler.events.list == [event]


def test_multiple_keys_that_are_long_overdue(throttler):
    # should be emitted all in one process call
    # and eviction should be applied
    throttler.target.new_event(Event('a', 'create'))
    throttler.target.new_event(Event('b', 'create'))
    throttler.target.process_queue()
    throttler.events.clear()

    throttler.time.add(timedelta(milliseconds=20))

    # these two will be withheld
    ea = Event('a', 'modify')
    eb = Event('b', 'modify')
    throttler.target.new_event(ea)
    throttler.target.new_event(eb)

    throttler.time.add(timedelta(milliseconds=40))
    throttler.target.process_queue()

    assert throttler.events.list == [ea, eb]
    assert throttler.target.next_action_delta() is None
