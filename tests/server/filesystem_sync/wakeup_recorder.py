class WakeupRecorder:
    def __init__(self):
        self.events = 0

    def call(self, debouncer):
        self.events += 1
