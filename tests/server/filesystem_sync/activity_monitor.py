from __future__ import annotations

from datetime import timedelta, datetime
from typing import Callable


class ActivityMonitor:

    def __init__(self, window: timedelta, time_func: Callable[[], datetime] = datetime.utcnow):
        super().__init__()
        self._last_touch: datetime | None = None
        self.window = window
        self._time_func = time_func

    def at_rest(self) -> bool:
        delta = self.rest_delta()
        if delta is None:
            # print('at_rest: True')
            return True
        ar = delta >= self.window
        # print(f'at_rest: {ar}')
        return ar

    def rest_delta(self) -> timedelta | None:
        lt = self._last_touch
        if lt is None:
            return None
        delta = self._time_func() - lt
        return delta

    def touch(self):
        self._last_touch = self._time_func()
