from datetime import datetime, timedelta


class EventObserver:
    _last_event: datetime
    _now: callable

    def __init__(self, min_delay_millis, time_provider=None):
        self._min_delay_millis = min_delay_millis
        if time_provider is None:
            time_provider = datetime.utcnow
        self._now = time_provider
        self._update()

    def _update(self):
        self._last_event = self._now()

    def event_happened(self):
        self._update()

    def is_stable(self):
        if self._min_delay_millis == 0:
            return True
        now = self._now()
        diff: timedelta = now - self._last_event
        return diff.total_seconds() * 1000 > self._min_delay_millis
