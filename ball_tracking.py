# Import necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from util import RGB

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file (optional)")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

pts = deque(maxlen=args["buffer"])

# If a video path was not supplied, grab a reference to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()
# Otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])
# Allow the camera or video file to warm up
time.sleep(2.0)

# Keep looping
while True:
    start_time = time.time()
    # Grab the current frame
    frame = vs.read()
    # Handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame
    # If we are viewing a video and we did not grab a frame, then we have reached the end of the video
    if frame is None:
        break
    # Resize the frame, blur it, and convert it to the HSV color space
    frame = imutils.resize(frame, width=420)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    # hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    rgb = blurred
    # Construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
    mask = cv2.inRange(rgb, RGB.WHITELOWER, RGB.WHITE)
    # mask = cv2.erode(mask, None, iterations=2)
    # mask = cv2.dilate(mask, None, iterations=2)

    # Find contours in the mask and initialize the current (x, y) center of the ball
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    # Only proceed if at least one contour was found
    if len(cnts) > 0:
        # Find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        M = cv2.moments(c)
        try:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        except ZeroDivisionError:
            continue

        # Only proceed if the radius meets a minimum size
        if radius > 10:
            # Draw the circle boundary and centroid on the frame, then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius), RGB.YELLOW, 1)
            cv2.circle(frame, center, 5, RGB.RED, -1)

        # Calculate FPS
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        print(f'x: {x:.2f}, y: {y:.2f}, fps: {fps:.2f}')

    # Update the points queue
    pts.appendleft(center)
    
    # Show the frame to our screen
    cv2.imshow("Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    # If the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break
# If we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()
# Otherwise, release the camera
else:
    vs.release()
# Close all windows
cv2.destroyAllWindows()
