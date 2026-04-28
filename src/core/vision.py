import threading, time, pygame

import cv2
import numpy as np

from src.core.laserbuffer import PointerState

class VisionCore:
    def __init__(self, laser_buffer, target_w, target_h):
        self.laser_buffer = laser_buffer
        self.target_w = target_w
        self.target_h = target_h

        self.pointer_state = PointerState
        self.running = False
        self.thread = None

        self.last_x = 0
        self.last_y = 0

        self.transform_matrix = None
        self.latest_frame = None

        self.camera_w = 1920
        self.camera_h = 1080

        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.transform_matrix = None
        self.calibration_points = []

    def start(self, camera_id):
        self.camera_id = camera_id
        self.running = True
        self.thread = threading.Thread(target=self.process_frames, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def process_frames(self):
        cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_h)

        lower_red1 = np.array([0, 100, 200])
        upper_red1 = np.array([20, 255, 255])

        lower_red2 = np.array([160, 100, 200])
        upper_red2 = np.array([180, 255, 255])

        while self.running:
            success, frame = cap.read()

            if success:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                with self.frame_lock:
                    self.latest_frame = rgb_frame

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                mask_1 = cv2.inRange(hsv, lower_red1, upper_red1)
                mask_2 = cv2.inRange(hsv, lower_red2, upper_red2)
                mask = cv2.bitwise_or(mask_1, mask_2)

                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                laser_visible = False

                if contours:
                    c = max(contours, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)

                    if radius > 3:
                        laser_visible = True

                        if self.transform_matrix is not None:
                            raw_point = np.array([[[x, y]]], dtype=np.float32)
                            transformed_point = cv2.perspectiveTransform(raw_point, self.transform_matrix)

                            mapped_x = int(transformed_point[0][0][0])
                            mapped_y = int(transformed_point[0][0][1])
                        else:
                            mapped_x = int((x / self.camera_w) * self.target_w)
                            mapped_y = int((y / self.camera_h) * self.target_h)

                        self.last_x = mapped_x
                        self.last_y = mapped_y

                current_state = PointerState(self.last_x, self.last_y, laser_visible, time.time())
                self.laser_buffer.put_latest(current_state)

            time.sleep(0.03)

        cap.release()

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
                [game_w, game_h],
                [0, game_h]
            ], dtype=np.float32)

            self.transform_matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
            print("VisionCore: Transform Matrix has generated")