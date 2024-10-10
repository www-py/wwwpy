from __future__ import annotations

from threading import Lock
from typing import Any, Callable, List
from datetime import datetime, timedelta


class Debouncer:
    def __init__(self, window: timedelta, wakeup: Callable[['Debouncer'], None] = None,
                 time_func: Callable[[], datetime] = datetime.utcnow):
        self.window = window
        self.wakeup = wakeup
        self._time_func = time_func
        self._events: List[Any] = []
        self._last_event_time: datetime | None = None
        self._lock = Lock()

    @property
    def is_debouncing(self) -> bool:
        """True if we were in active window OR we have events yet to be emitted."""
        with self._lock:
            return self._last_event_time is not None

    def add_event(self, event: Any) -> None:
        """Add an event to the debouncer.
        If the event is the first event in the window, wakeup() will be called to signal that the waiting time is changed.
        """
        with self._lock:
            current_time = self._time_func()
            self._events.append(event)
            self._last_event_time = current_time
            if len(self._events) == 1:
                self.wakeup(self)

    def events(self) -> List[Any]:
        with self._lock:
            emission = self._time_until_next_emission()
            if emission is None or emission > timedelta(0):
                return []

            events_to_emit = self._events.copy()
            self._events.clear()
            self._last_event_time = None

            return events_to_emit

    def time_until_next_emission(self) -> timedelta:
        with self._lock:
            return self._time_until_next_emission()

    def _time_until_next_emission(self) -> timedelta:
        if not self._events or self._last_event_time is None:
            return self.window

        current_time = self._time_func()
        time_since_last_event = current_time - self._last_event_time
        time_remaining = self.window - time_since_last_event

        return time_remaining
