import threading, queue, time

class PointerState:
    def __init__(self, x: float, y: float, laser_visible: bool, timestamp: float):
        self.x = x
        self.y = y
        self.laser_visible = laser_visible
        self.timestamp = timestamp

class LaserBuffer:
    def __init__(self):
        self.buffer = queue.LifoQueue(maxsize=1)
        self.lock = threading.Lock()

        self.last_state = PointerState(0.0, 0.0, False, 0.0)

    def put_latest(self, state: PointerState):
        with self.lock:
            if self.buffer.full():
                try:
                    self.buffer.get_nowait()
                except queue.Empty:
                    pass

            self.buffer.put(state)

    def get_latest(self) -> PointerState:
        with self.lock:
            try:
                new_state = self.buffer.get_nowait()

                self.last_state = new_state

                return new_state
            except queue.Empty:
                return self.last_state