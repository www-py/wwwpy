from datetime import datetime
from time import sleep

from tests import timeout_multiplier
from wwwpy.common.event_observer import EventObserver
from wwwpy.server import watcher


def test_watcher_delayed(tmp_path):
    file = tmp_path / 'file.txt'
    file.write_text('hello')
    events = []
    prev = datetime.utcnow()

    def callback(event):
        nonlocal prev
        utcnow = datetime.utcnow()
        delta = utcnow - prev
        prev = utcnow
        events.append((delta, event))

    target = watcher.ChangeHandler(tmp_path, callback)
    target.watch_directory()

    file.write_text('world')
    event_observer = EventObserver(100 * timeout_multiplier())
    [sleep(0.1) for _ in range(10) if not event_observer.is_stable()]
    for e in events:
        print(e)

    assert len(events) == 1
    assert events[0][1].src_path == str(file)
