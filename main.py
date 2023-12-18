from time import time

from controller import PIDController, ServoController
from tracker import BallTracker


GPIO_PIN_X = 17
GPIO_PIN_Y = 18


# Calibration
with open("calibration.txt", "r") as f:
    line = f.readline()
    OFFSET_X, OFFSET_Y, *_ = line.strip().split(", ")
    OFFSET_X = float(OFFSET_X) * 10
    OFFSET_Y = float(OFFSET_Y) * 10


# Center
# freq = 1; target_position = [[170, 170]]

# Rectangle
freq = 4; target_position = [[120, 120],[220,120],[220,220],[120,220]]

# Circle, radius 40, center (170, 170), 60 points
# freq = 0.3; target_position = [(210, 170), (210, 174), (209, 178), (208, 183), (206, 187), (204, 190), (202, 194), (199, 197), (196, 200), (193, 203), (189, 205), (186, 207), (182, 208), (177, 209), (173, 210), (169, 210), (165, 210), (161, 209), (156, 208), (153, 206), (149, 204), (145, 201), (142, 199), (139, 196), (137, 192), (135, 188), (133, 185), (131, 181), (131, 176), (130, 172), (130, 168), (131, 164), (131, 159), (133, 155), (135, 152), (137, 148), (139, 144), (142, 141), (145, 139), (149, 136), (153, 134), (156, 132), (161, 131), (165, 130), (169, 130), (173, 130), (177, 131), (182, 132), (186, 133), (189, 135), (193, 137), (196, 140), (199, 143), (202, 146), (204, 150), (206, 153), (208, 157), (209, 162), (210, 166), (210, 170)]

tracker = BallTracker()
tracker.start()
pd_ctl = PIDController(kp_x=8, ki_x=0.000, kd_x=140, kp_y=8, ki_y=0.000, kd_y=140)
servo_ctl = ServoController(pin_x=GPIO_PIN_X, pin_y=GPIO_PIN_Y)

t = time()
while True:
    now = time()
    pos_idx = int((now - t) / freq) % len(target_position)

    pd_ctl.set_target_position(target_position[pos_idx])
    tracker.set_target_position(target_position[pos_idx])

    tracker.process_frame()
    position = tracker.get_position()
    if position is None:
        continue

    pd_ctl.update(position)
    output = pd_ctl.get_output()
    if output is None:
        continue

    print(f"tgt: {target_position[pos_idx]}, pos: {position}, fps: {1/(time()-now):.2f}, out: {output}")
    servo_ctl.set_angle(GPIO_PIN_X, output[0] + OFFSET_X)
    servo_ctl.set_angle(GPIO_PIN_Y, output[1] + OFFSET_Y)

servo_ctl.cleanup()
