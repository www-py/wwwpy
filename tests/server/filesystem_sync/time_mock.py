from datetime import datetime, timedelta


class TimeMock:
    def __init__(self):
        self.now = datetime(2023, 1, 1, 0, 0, 0)

    def reset(self):
        self.now = datetime(2023, 1, 1, 0, 0, 0)

    def __call__(self):
        return self.now

    def advance(self, delta: timedelta):
        self.now += delta
