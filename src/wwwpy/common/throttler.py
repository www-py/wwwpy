from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from queue import PriorityQueue
from threading import Lock
from typing import Any, Callable, Dict


class State(Enum):
    FIRST = 1
    THROTTLE = 2
    DELAYED = 3


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
            emit: Callable[[Event], None],
            time_provider: Callable[[], datetime]):
        """A wakeup call should wake up the thread. The thread should call process_queue to process the events.
        and then go to sleep accordingly to next_action_delta."""
        if time_provider is None:
            time_provider = datetime.utcnow
        self._time_provider = time_provider
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
                prev_evt.state = State.DELAYED

            self.wakeup()

    def process_queue(self):
        def done():
            delta = self.next_action_delta()
            return delta is None or delta.total_seconds() > 0

        while not done():
            with self._lock:

                evt = self._queue.get()
                if evt.state == State.FIRST:
                    evt.state = State.THROTTLE
                    evt.action_time += timedelta(milliseconds=self._timeout_millis)
                    self._queue.put(evt)
                else:
                    del self._states[evt.event.key]
                    if evt.state == State.DELAYED:
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

    def wakeup(self):
        raise NotImplementedError
