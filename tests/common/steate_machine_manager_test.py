from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from queue import PriorityQueue
from typing import Any, Callable, Dict

import pytest

from enum import Enum
import pytest


class State(Enum):
    OPEN = 1
    LOADED = 2
    THROTTLE = 3


class StateMachine:
    def __init__(self):
        self.state = State.OPEN

    def event(self) -> bool:
        if self.state == State.OPEN:
            self.state = State.THROTTLE
            return True
        elif self.state == State.THROTTLE:
            self.state = State.LOADED
            return False
        elif self.state == State.LOADED:
            return False

    def timeout(self) -> bool:
        if self.state == State.THROTTLE:
            self.state = State.OPEN
            return False
        elif self.state == State.LOADED:
            self.state = State.OPEN
            return True


@pytest.fixture
def state_machine():
    return StateMachine()


def test_initial_state_transition(state_machine):
    assert state_machine.state == State.OPEN
    result = state_machine.event()
    assert state_machine.state == State.THROTTLE
    assert result is True


def test_throttling_state_transition(state_machine):
    state_machine.state = State.THROTTLE
    result = state_machine.event()
    assert state_machine.state == State.LOADED
    assert result is False


def test_timeout_in_throttling_state(state_machine):
    state_machine.state = State.THROTTLE
    result = state_machine.timeout()
    assert state_machine.state == State.OPEN
    assert result is False


def test_timeout_in_loaded_state(state_machine):
    state_machine.state = State.LOADED
    result = state_machine.timeout()
    assert state_machine.state == State.OPEN
    assert result is True


def test_event_in_loaded_state(state_machine):
    state_machine.state = State.LOADED
    result = state_machine.event()
    assert state_machine.state == State.LOADED
    assert result is False


@dataclass
class Event:
    key: Any = field()
    item: Any = field()


@dataclass(order=True)
class _EventState:
    action_time: datetime = field()
    event: Event = field(compare=False)
    state: State = field(compare=False, default=State.THROTTLE)


class EventThrottler:
    def __init__(
            self, timeout_millis: int,
            emit: Callable[[Any], None],
            time_provider: Callable[[], datetime],
            wakeup: Callable[[], None] = None):
        if time_provider is None:
            time_provider = datetime.utcnow
        if wakeup is None:
            wakeup = lambda: None
        self._wakeup = wakeup
        self._time_provider: datetime = time_provider
        self._emit = emit
        self._timeout_millis = timeout_millis
        self._queue: PriorityQueue[_EventState] = PriorityQueue()
        self._states: Dict[Any, _EventState] = {}

    def new_event(self, event: Event):
        prev_evt = self._states.get(event.key, None)
        if prev_evt is None:
            wakeup_time = self._time_provider() + timedelta(milliseconds=self._timeout_millis)
            state = _EventState(wakeup_time, event)
            self._states[event.key] = state
            self._queue.put(state)
            self._emit(event)
        else:
            assert prev_evt.event.key == event.key
            prev_evt.event = event
            prev_evt.state = State.LOADED

        self._wakeup()

    def process_queue(self):
        delta = self.next_action_delta()
        if delta is None or delta.total_seconds() > 0:
            return

        evt = self._queue.get()
        if evt.state == State.LOADED:
            del self._states[evt.event.key]
            self._emit(evt.event)

    def next_action_delta(self) -> timedelta | None:
        if self._queue.empty():
            return None
        evt = self._queue.queue[0]
        diff = evt.action_time - self._time_provider()
        return diff


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
        self.access_requests = []
        self.events = EventRecorder()
        self.time = TimeMock()
        self.target = EventThrottler(50, self.events.append, self.time.time, self._assess_request)

    def _assess_request(self):
        # self.access_requests.append(self.target.wait_to_next())
        self.access_requests.append(None)

    def assess_count(self):
        return len(self.access_requests)


@pytest.fixture
def throttler():
    return ThrottlerFixture()


def test_event_manager(throttler):
    e1 = Event('a', 'create')
    throttler.target.new_event(e1)
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
    assert throttler.target.next_action_delta() == timedelta(milliseconds=50)


def test_emit_after_throttling(throttler):
    throttler.target.new_event(Event('a', 'create'))

    throttler.time.add(timedelta(milliseconds=40))

    e2 = Event('a', 'modify')
    throttler.target.new_event(e2)

    throttler.time.add(timedelta(milliseconds=11))

    throttler.events.list.clear()
    throttler.target.process_queue()
    assert throttler.events.list == [e2]


def test_emit_after_discarding_one_event(throttler):
    throttler.target.new_event(Event('a', 'create'))

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
    assert throttler.assess_count() == 0
    throttler.target.new_event(Event('a', 'create'))
    assert throttler.assess_count() == 1


def test_eviction(throttler):
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


def test_multiple_keys_that_are_long_overdue():
    # should be emitted all in one process call
    # and eviction should be applied
    pass
