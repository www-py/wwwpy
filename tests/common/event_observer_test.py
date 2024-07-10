from datetime import datetime, timedelta

from wwwpy.common.event_observer import EventObserver


def test_not_enough_time_passed_for_stability():
    now = datetime(2021, 1, 1, 0, 0, 0)
    target = EventObserver(100, lambda: now)
    assert not target.is_stable()


def test_enough_time_passed_for_stability():
    now = datetime(2021, 1, 1, 0, 0, 0)

    def time_provider():
        nonlocal now
        return now

    target = EventObserver(100, time_provider)
    now = now + timedelta(milliseconds=101)
    assert target.is_stable()

def test_event_delay_stability():
    now = datetime(2021, 1, 1, 0, 0, 0)

    def time_provider():
        nonlocal now
        return now

    target = EventObserver(100, time_provider)
    now = now + timedelta(milliseconds=50)
    target.event_happened()
    now = now + timedelta(milliseconds=70)
    assert not target.is_stable()
    now = now + timedelta(milliseconds=70)
    assert target.is_stable()
