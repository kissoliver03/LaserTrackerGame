import threading, time, pygame
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

from src.core.laserbuffer import PointerState, LaserBuffer

class VisionCore:
    def __init__(self, active_sources, target_w, target_h):
        self.active_sources = active_sources if active_sources is not None else []
        self.target_w = target_w
        self.target_h = target_h

        self.buffers = {source: LaserBuffer() for source in self.active_sources}
        self.last_positions = {source: (0, 0) for source in self.active_sources}

        self.running = False
        self.thread = None
        self.executor = None

        self.last_x = 0
        self.last_y = 0

        self.camera_w = 800
        self.camera_h = 600

        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.transform_matrix = None
        self.calibration_points = []

        self.color_bounds = {
            "laser_red": [
                (np.array([0, 150, 180]), np.array([20, 255, 255])),
                (np.array([160, 50, 180]), np.array([180, 255, 255]))
            ],
            "laser_green": [
                (np.array([35, 50, 150]), np.array([90, 255, 255]))
            ]
        }

    def start(self, camera_id):
        self.camera_id = camera_id
        self.running = True

        self.executor = ThreadPoolExecutor(max_workers=2)

        self.thread = threading.Thread(target=self.process_frames, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.executor:
            self.executor.shutdown()

    def process_color_worker(self, hsv_frame, source):
        bounds = self.color_bounds.get(source)
        if not bounds:
            return

        if len(bounds) == 2:
            mask_1 = cv2.inRange(hsv_frame, bounds[0][0], bounds[0][1])
            mask_2 = cv2.inRange(hsv_frame, bounds[1][0], bounds[1][1])
            mask = cv2.bitwise_or(mask_1, mask_2)
        else:
            mask = cv2.inRange(hsv_frame, bounds[0][0], bounds[0][1])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        laser_visible = False

        last_x, last_y = self.last_positions[source]
        mapped_x, mapped_y = last_x, last_y

        if contours:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)

            if radius > 1:
                laser_visible = True

                if self.transform_matrix is not None:
                    raw_point = np.array([[[x, y]]], dtype=np.float32)
                    transformed_point = cv2.perspectiveTransform(raw_point, self.transform_matrix)
                    mapped_x = int(transformed_point[0][0][0])
                    mapped_y = int(transformed_point[0][0][1])
                else:
                    mapped_x = int((x / self.camera_w) * self.target_w)
                    mapped_y = int((y / self.camera_h) * self.target_h)

        self.last_positions[source] = (mapped_x, mapped_y)
        current_state = PointerState(mapped_x, mapped_y, laser_visible, time.time())
        self.buffers[source].put_latest(current_state)

    def process_frames(self):
        cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_h)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FPS, 30)

        while self.running:
            success, frame = cap.read()

            if success:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                with self.frame_lock:
                    self.latest_frame = rgb_frame

                blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)

                hsv = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

                for sources in self.active_sources:
                    self.executor.submit(self.process_color_worker, hsv, sources)

        cap.release()

    def set_active_sources(self, sources):
        self.active_sources = sources

        for source in self.active_sources:
            if source not in self.buffers:
                self.buffers[source] = LaserBuffer()
                self.last_positions[source] = (0, 0)

    def get_buffer(self, source_name):
        return self.buffers.get(source_name)

    def reset_calibration(self):
        self.calibration_points = []
        self.transform_matrix = None

    def add_calibration_point(self, x, y):
        if len(self.calibration_points) < 4:
            self.calibration_points.append((x, y))

    def finalize_calibration(self, game_w, game_h):
        if len(self.calibration_points) == 4:
            pts_src = np.array(self.calibration_points, dtype=np.float32)
            pts_dst = np.array([
                [0, 0],
                [game_w, 0],
                [0, game_h],
                [game_w, game_h],
            ], dtype=np.float32)

            self.transform_matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
            print("VisionCore: Transform Matrix has generated")
        else:
            print('VisionCore: Calibration has been not successful')