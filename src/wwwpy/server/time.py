import datetime as datetime_mod
import time
from datetime import datetime, date, timedelta
from typing import Union, Optional


def time_wrapper(above_seconds=0.0, callback=None, *outer_args, **outer_kwargs):
    def decorator(function):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = function(*args, **kwargs)
            end = time.time()
            delta_secs = (end - start)
            if delta_secs >= above_seconds:
                if callback is None:
                    print('{:s} function took {:.3f} ms'.format(function.__name__, delta_secs * 1000.0))
                else:
                    callback(delta_secs, *args)
            return result

        return wrapper

    return decorator


def time_wrapper_old(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        ret = f(*args, **kwargs)
        end = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (end - start) * 1000.0))
        return ret

    return wrapper


def wait_until(end: Union[date, datetime]):
    """
    When the function ends, it will be a little after `end`
    """
    if isinstance(end, date) and not isinstance(end, datetime):
        end = datetime.combine(end, datetime.min.time())
    if not isinstance(end, datetime):
        raise Exception(f'Argument needs to be a date or a datetime. It is a type={type(end)} value={end}')

    while True:
        diff = (end - datetime.now()).total_seconds()
        if diff < 0:  # will return after now is after the wait point in time
            return
        print(f'wait_until({end}) diff={diff} sleeping diff/2...')
        time.sleep(diff / 2)


def first_day_next_month(today: Optional[date] = None) -> date:
    if today is None:
        today = date.today()
    dt = today
    while dt.day != 1 or dt.month == today.month:
        dt = dt + timedelta(days=1)
    return dt


def main_harness():
    now = datetime.now()
    nt = now + timedelta(seconds=2)
    new_time = datetime_mod.time(nt.hour, nt.minute, nt.second)
    dt = datetime.combine(now.date(), new_time)
    wait_until(dt)
    now = datetime.now()
    print(f'one second is passed diff={dt - now}  dt={dt} now={now}')
    dt = datetime.combine(first_day_next_month(), datetime_mod.time(9, 30, 0))
    print(dt)
    wait_until(dt)


if __name__ == '__main__':
    main_harness()
