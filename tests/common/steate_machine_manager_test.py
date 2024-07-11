from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from queue import PriorityQueue
from threading import Lock
from typing import Any, Callable, Dict, List

import pytest

from enum import Enum
import pytest


class State(Enum):
    OPEN = 1
    LOADED = 2
    THROTTLE = 3
    FIRST = 4


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
    state: State = field(compare=False, default=State.FIRST)


class EventThrottler:
    def __init__(
            self, timeout_millis: int,
            emit: Callable[[Any], None],
            time_provider: Callable[[], datetime],
            wakeup: Callable[[], None] = None):
        """A wakeup call should wake up the thread. The thread should call process_queue to process the events.
        and then go to sleep accordingly to next_action_delta."""
        if time_provider is None:
            time_provider = datetime.utcnow
        if wakeup is None:
            wakeup = lambda: None
        self._wakeup = wakeup
        self._time_provider: datetime = time_provider
        self._emit = emit
        self._timeout_millis = timeout_millis

        # The following two data structure needs to be intended as a single atomic datastructure
        # if an item appears/disappear from one it should appear/disappear from the other
        self._queue: PriorityQueue[_EventState] = PriorityQueue()
        self._states: Dict[Any, _EventState] = {}
        self._lock = Lock()

    def new_event(self, event: Event):
        with self._lock:
            prev_evt = self._states.get(event.key, None)
            if prev_evt is None:
                state = _EventState(self._time_provider(), event)  # add for immediate emit
                self._states[event.key] = state
                self._queue.put(state)
            else:
                assert prev_evt.event.key == event.key
                prev_evt.event = event
                prev_evt.state = State.LOADED

            self._wakeup()

    def process_queue(self):
        while not self._queue.empty():
            with self._lock:

                delta = self.next_action_delta()
                if delta is None or delta.total_seconds() > 0:
                    return

                evt = self._queue.get()
                if evt.state == State.FIRST:
                    evt.state = State.THROTTLE
                    evt.action_time += timedelta(milliseconds=self._timeout_millis)
                    self._queue.put(evt)
                else:
                    del self._states[evt.event.key]
                    if evt.state == State.LOADED:
                        pass  # we need to emit this
                    elif evt.state == State.THROTTLE:
                        evt = None  # we already emitted when it was in FIRST state

            if evt is not None:
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
        self.wakeup_requests = []
        self.events = EventRecorder()
        self.time = TimeMock()
        self.target = EventThrottler(50, self.events.append, self.time.time, self._wakeup)

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
