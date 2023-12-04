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

        self.window_size = 300
        self.x_pos = 0
        self.y_pos = 0

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

    def process_frame(self):
        frame = self.vs.read()
        frame = frame[1] if self.video_path else frame
        if frame is None:
            return
        frame = imutils.resize(frame, height=self.window_size+100)
        frame = frame[
            self.x_pos : self.x_pos + self.window_size,
            self.y_pos : self.y_pos + self.window_size,
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
                cv2.circle(frame, self.position, 5, RGB.RED, -1)
            if self.target_position:
                cv2.circle(frame, self.target_position, 5, RGB.BLUE, -1)
        self.pts.appendleft(self.position)
        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            self.stop()
        # elif cv2.waitKey(1) & 0xFF == ord("h"):
        #     self.x_pos = min(self.x_pos - 10, 0)
        # elif cv2.waitKey(1) & 0xFF == ord("j"):
        #     self.y_pos = min(self.y_pos - 10, 0)
        # elif cv2.waitKey(1) & 0xFF == ord("k"):
        #     self.y_pos = self.y_pos + 10
        # elif cv2.waitKey(1) & 0xFF == ord("l"):
        #     self.x_pos = self.x_pos + 10

    def get_position(self):
        return self.position

    def set_target_position(self, position):
        self.target_position = position


if __name__ == "__main__":
    tracker = BallTracker()
    tracker.start()
    while True:
        start_time = time.time()
        tracker.process_frame()
        end_time = time.time()

        fps = 1 / (end_time - start_time)
        position = tracker.get_position()
        if position:
            print(f"x: {position[0]}, y: {position[1]}, fps: {fps:.2f}")
