import os
import time
from collections import deque

import cv2
import imutils
from imutils.video import VideoStream

from util import RGB


class BallTracker:
    def __init__(self, video_path=None, buffer_size=64):
        self.video_path = video_path
        self.buffer_size = buffer_size
        self.vs = None
        self.pts = deque(maxlen=self.buffer_size)

        self.position = None
        self.target_position = None

        self.window_size = 320
        self.x_pos = 100
        self.y_pos = 100
        self.angle = 0

        if os.path.exists("calibration.txt"):
            with open("calibration.txt", "r") as f:
                line = f.readline()
                _, _, x_pos, y_pos, angle = line.strip().split(", ")
                self.x_pos = int(x_pos)
                self.y_pos = int(y_pos)
                self.angle = int(angle)

    def __del__(self):
        self.stop()

    def start(self):
        if self.video_path is None:
            self.vs = VideoStream(src=0).start()
        else:
            self.vs = cv2.VideoCapture(self.video_path)
        time.sleep(2.0)

    def stop(self):
        if self.video_path is None:
            self.vs.stop()
        else:
            self.vs.release()
        cv2.destroyAllWindows()
    
    def cap(self, pos: int):
        if pos < 0:
            return 0
        elif pos > 120:
            return 300
        else:
            return pos

    def process_frame(self):
        frame = self.vs.read()
        frame = frame[1] if self.video_path else frame
        if frame is None:
            return
        frame = imutils.resize(frame, height=400)
        frame = imutils.rotate_bound(frame, self.angle)
        frame = frame[
            self.y_pos : self.y_pos + self.window_size,
            self.x_pos : self.x_pos + self.window_size,
        ]
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        rgb = blurred
        mask = cv2.inRange(rgb, RGB.WHITELOWER, RGB.WHITE)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            try:
                self.position = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            except ZeroDivisionError:
                return
            if radius > 10:
                cv2.circle(frame, (int(x), int(y)), int(radius), RGB.YELLOW, 1)
                cv2.circle(frame, self.position, 2, RGB.RED, -1)
            if self.target_position:
                cv2.circle(frame, self.target_position, 2, RGB.BLUE, -1)
            
            # draw blue square 300 by 300
            cv2.rectangle(frame, (20, 20), (300, 300), RGB.BLUE, 2)
        self.pts.appendleft(self.position)
        cv2.imshow("Frame", frame)
       
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            self.stop()
        elif key == ord("h"):
            self.x_pos = self.cap(self.x_pos - 5)
        elif key == ord("j"):
            self.y_pos = self.cap(self.y_pos + 5)
        elif key == ord("k"):
            self.y_pos = self.cap(self.y_pos - 5)
        elif key == ord("l"):
            self.x_pos = self.cap(self.x_pos + 5)
        elif key == ord("="):
            self.window_size = self.window_size + 5
        elif key == ord("-"):
            self.window_size = self.window_size - 5
        elif key == ord("r"):
            self.angle = self.angle + 1
        elif key == ord("t"):
            self.angle = self.angle - 1

    def get_position(self):
        return self.position

    def set_target_position(self, position):
        self.target_position = position


if __name__ == "__main__":
    tracker = BallTracker()
    tracker.start()

    try:
        while True:
            start_time = time.time()
            tracker.process_frame()
            end_time = time.time()

            fps = 1 / (end_time - start_time)
            position = tracker.get_position()
            if position:
                print(f"x: {position[0]}, y: {position[1]}, wx: {tracker.x_pos}, wy: {tracker.y_pos}, fps: {fps:.2f}")
    except KeyboardInterrupt:
        tracker.stop()

        print("Calibration")
        print(f"x: {tracker.x_pos}, y: {tracker.y_pos}, angle: {tracker.angle}")

        yn = input("Save? (y/N): ")
        if yn in ["y", "Y"]:
            if not os.path.exists("calibration.txt"):
                with open("calibration.txt", "w") as f:
                    f.write(f"90, 90, {tracker.x_pos}, {tracker.y_pos}, {tracker.angle}")

            else:
                with open("calibration.txt", "r") as f:
                    lines = f.readline().strip().split(", ")
                with open("calibration.txt", "w") as f:
                    f.write(f"{lines[0]}, {lines[1]}, {tracker.x_pos}, {tracker.y_pos}, {tracker.angle}")
        else:
            print("Exiting...")