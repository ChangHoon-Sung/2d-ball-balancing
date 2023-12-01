from controller import PDController, ServoController
from tracker import BallTracker


tracker = BallTracker()
tracker.start()

controller = PDController(kp=1.0, kd=0.1)
controller.set_desired_position((0, 0))  # Set desired position to (0, 0)

servo = ServoController(pin_x=18, pin_y=19)

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
