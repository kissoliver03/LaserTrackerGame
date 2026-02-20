import threading, time, pygame
from src.classes.laserbuffer import LaserBuffer, PointerState

class VisionCore:
    def __init__(self, laser_buffer):
        self.laserBuffer = laser_buffer
        self.pointerState = PointerState
        self.running = False
        self.thread = None

        self.last_x = 0
        self.last_y = 0

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.process_frames, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def process_frames(self):
        while self.running:
            if pygame.display.get_init():

                laser_visible = pygame.mouse.get_pressed()[0]

                if laser_visible:
                    self.last_x, self.last_y = pygame.mouse.get_pos()

                current_state = PointerState(self.last_x, self.last_y, laser_visible, time.time())

                self.laserBuffer.put_latest(current_state)

                time.sleep(0.0416)
