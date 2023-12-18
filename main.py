from controller import PIDController, ServoController
from tracker import BallTracker


GPIO_PIN_X = 17
GPIO_PIN_Y = 18

target_position = (170, 150)

tracker = BallTracker()
tracker.start()

pd_ctl = PIDController(kp_x=0.5, ki_x=0, kd_x=7, kp_y=0.5, ki_y=0, kd_y=7)
pd_ctl.set_desired_position(target_position)

servo_ctl = ServoController(pin_x=GPIO_PIN_X, pin_y=GPIO_PIN_Y)

while True:
    tracker.process_frame()
    position = tracker.get_position()
    if position is None:
        continue
    pd_ctl.update(position)  # Update controller with position
    output = pd_ctl.get_output()
    if output is None:
        continue

    print(f"tgt: {target_position}, pos: {position}, out: {output}")
    servo_ctl.set_angle(GPIO_PIN_X, output[0] + 90)
    servo_ctl.set_angle(GPIO_PIN_Y, output[1] + 90)

servo_ctl.cleanup()
