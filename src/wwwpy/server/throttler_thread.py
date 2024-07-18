from threading import Thread, Event
from typing import Callable

from wwwpy.common.throttler import EventThrottler


class EventThrottlerThread(EventThrottler):
    def __init__(self, max_delay_millis, emit: Callable[[Event], None], time_provider):
        self._thread = Thread(daemon=True, target=self._thread_loop, name='EventThrottlerThread')
        self._event = Event()
        super().__init__(max_delay_millis, emit, time_provider)
        self._thread.start()

    def wakeup(self):
        self._event.set()

    def _thread_loop(self):
        while self._thread is not None:
            delta = self.next_action_delta()
            timeout_millis = None if delta is None else delta.total_seconds() * 1000
            self._event.wait(timeout_millis)
            self._event.clear()
            self.process_queue()

    def stop_join(self):
        t = self._thread
        self._thread = None
        self.wakeup()
        t.join()
