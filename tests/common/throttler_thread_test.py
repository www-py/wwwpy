from __future__ import annotations

from datetime import datetime, timedelta
from time import sleep

import pytest

from tests.common.throttler_test import EventRecorder, TimeMock
from wwwpy.common.throttler import EventThrottler, Event
from wwwpy.server.throttler_thread import EventThrottlerThread


class ThrottlerThreadFixture:

    def __init__(self):
        self.wakeup_requests = []
        self.events = EventRecorder()
        self.time = TimeMock()
        self.target = EventThrottlerThread(50, self.events.append, self.time.time)


@pytest.fixture
def throttler():
    fixture = ThrottlerThreadFixture()
    yield fixture
    fixture.target.stop_join()


def test_event(throttler):
    e1 = Event('a', 'create')
    throttler.target.new_event(e1)
    [sleep(0.1) for _ in range(10) if not throttler.events.list]
    assert throttler.events.list == [e1]
