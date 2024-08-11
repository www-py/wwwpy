from __future__ import annotations

import threading
from datetime import timedelta
from threading import Thread, Event
from time import sleep
from typing import Callable, Any, List

from wwwpy.server.filesystem_sync.debouncer import Debouncer


class DebouncerThread:

    def __init__(self, debouncer: Debouncer, emit: Callable[[List[Any]], None]):
        self._debouncer = debouncer
        self._emit = emit
        self._event = Event()
        debouncer.wakeup = self._wakeup
        self._continue = True
        self._thread: Thread | None = None

    def _wakeup(self, debouncer: Debouncer | None):
        self._event.set()

    def _thread_loop(self):
        while self._continue:
            delta = self._debouncer.time_until_next_emission()
            timeout_millis = 1 if delta is None else delta.total_seconds()
            self._event.wait(timeout_millis)
            self._event.clear()
            events = self._debouncer.events()
            if events:
                self._emit(events)
        self._thread = None

    def start(self):
        if self._thread is not None:
            raise RuntimeError('Thread already started')
        self._continue = True
        self._thread = Thread(daemon=True, target=self._thread_loop, name='DebouncerThread')
        self._thread.start()

    def stop(self):
        self._continue = False
        self._wakeup(None)

    def join(self):
        t = self._thread
        if t is not None:
            t.join()

def main():
    debouncer = Debouncer(timedelta(milliseconds=100))

    def print_events(events):
        print('=' * 20 + f' current thread name={threading.current_thread().name}')
        print(f'len={len(events)} events={events}')

    debouncer_thread = DebouncerThread(debouncer, print_events)
    counter = 0

    def next_event():
        nonlocal counter
        counter += 1
        return f"e{counter}"

    def send(n, between, final):
        for _ in range(n, ):
            debouncer.add_event(next_event())
            sleep(between)
        sleep(final)

    for t in range(10):
        send(5, 0.09, 1)
        send(100, 0.01, 0.3)
        send(10, 0.05, 0.5)

    debouncer_thread.stop_join()


if __name__ == '__main__':
    main()
