from controller import PDController, ServoController
from tracker import BallTracker


GPIO_PIN_X = 18
GPIO_PIN_Y = 19

tracker = BallTracker()
tracker.start()

controller = PDController(kp_x=0.1, kd_x=0.1, kp_y=0.1, kd_y=0.1)
controller.set_desired_position((0, 0))  # Set desired position to (0, 0)

servo = ServoController(pin_x=GPIO_PIN_X, pin_y=GPIO_PIN_Y)

while True:
    tracker.process_frame()
    position = tracker.get_position()
    if position is None:
        continue
    controller.update(position)  # Update controller with position
    output = controller.get_output()
    if output is None:
        continue
    servo.set_angle(output[0], output[1])  # Set servo angles based on controller output
servo.cleanup()
