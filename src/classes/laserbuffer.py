import threading, queue

class PointerState:
    def __init__(self, x: float, y: float, laser_visible: bool, timestamp: float):
        self.x = x
        self.y = y
        self.laser_visible = laser_visible
        self.timestamp = timestamp

class LaserBuffer:
    def __init__(self):
        self.laser_buffer = queue.LifoQueue(maxsize=1)
        self.lock = threading.Lock()

        self.pointer_state = PointerState(0.0, 0.0, False, 0.0)

    def put_latest(self, state: PointerState):
        with self.lock:
            if self.laser_buffer.full():
                try:
                    self.laser_buffer.get_nowait()
                except queue.Empty:
                    pass

            self.laser_buffer.put(state)

    def get_latest(self) -> PointerState:
        with self.lock:
            try:
                new_state = self.laser_buffer.get_nowait()

                self.pointer_state = new_state

                return new_state
            except queue.Empty:
                return self.pointer_state