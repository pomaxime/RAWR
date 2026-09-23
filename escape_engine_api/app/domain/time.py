import time

from .item import Item


class Time(Item):
    def __init__(self, id: str, name: str, description: str, duration: int):
        super().__init__(id=id, name=name, description=description, item_type="timer")
        self.duration = duration
        self.start_time = None
        self.end_time = None
        self.running = False

    def start(self):
        if self.running:
            return
        self.start_time = time.monotonic()
        self.end_time = None
        self.running = True

    def stop(self):
        if self.running:
            self.end_time = time.monotonic()
            self.running = False
        elif self.end_time is None:
            self.end_time = self.start_time

    def elapsed(self):
        if self.start_time is None:
            return 0

        current_time = (
            time.monotonic() if self.running else (self.end_time or self.start_time)
        )
        return max(0.0, current_time - self.start_time)

    def remaining(self):
        return max(0, self.duration - int(self.elapsed()))
