import os
from typing import Tuple

import pigpio  # sudo apt-get install python3-pigpio && pip3 install pigpio


class PIDController:
    def __init__(self, kp_x: float, kd_x: float, ki_x: float, kp_y: float, kd_y: float, ki_y: float):
        self.kp_x: float = kp_x
        self.kd_x: float = kd_x
        self.ki_x: float = ki_x
        self.kp_y: float = kp_y
        self.kd_y: float = kd_y
        self.ki_y: float = ki_y
        self.desired_position: Tuple[float, float] = (None, None)
        self.current_position: Tuple[float, float] = (None, None)
        self.previous_error: Tuple[float, float] = (None, None)
        self.integral: Tuple[float, float] = (0, 0)
        self.output: Tuple[float, float] = (None, None)

    def set_desired_position(self, position: Tuple[float, float]):
        self.desired_position = position

    def update(self, position: Tuple[float, float]):
        self.current_position = position

        if None in self.desired_position or None in self.current_position:
            return

        error_x = self.desired_position[0] - self.current_position[0]
        error_y = self.desired_position[1] - self.current_position[1]

        if None in self.previous_error:
            derivative_x = 0
            derivative_y = 0
        else:
            derivative_x = error_x - self.previous_error[0]
            derivative_y = error_y - self.previous_error[1]

        self.integral = (self.integral[0] + error_x, self.integral[1] + error_y)

        self.output = (
            self.kp_x * error_x + self.kd_x * derivative_x + self.ki_x * self.integral[0],
            self.kp_y * error_y + self.kd_y * derivative_y + self.ki_y * self.integral[1],
        )
        self.previous_error = (error_x, error_y)

    def get_output(self) -> Tuple[float, float]:
        return self.output


class ServoController:
    def __init__(self, pin_x: int = 17, pin_y: int = 18):
        # run sudo pigpiod to start the pigpio daemon
        # os.system("sudo pigpiod")

        self.FREQENCY = 50  # Hz
        self.LOW_POS = 600  # 0 degrees
        self.HIGH_POS = 2400  # 180 degrees

        self.LEVEL_POS_X = 1500  # 90 degrees
        self.LEVEL_POS_Y = 1500  # 90 degrees

        if os.path.exists("calibration.txt"):
            with open("calibration.txt", "r") as f:
                line = f.readline()
                if line:
                    angle_x, angle_y, *_ = line.strip().split(", ")
                    self.LEVEL_POS_X = self.LOW_POS + float(angle_x) * 10
                    self.LEVEL_POS_Y = self.LOW_POS + float(angle_y) * 10

        self.pin_x = pin_x
        self.pin_y = pin_y

        self.pwm = pigpio.pi()

        self.pwm.set_mode(self.pin_x, pigpio.OUTPUT)
        self.pwm.set_mode(self.pin_y, pigpio.OUTPUT)

        self.pwm.set_PWM_frequency(self.pin_x, self.FREQENCY)
        self.pwm.set_PWM_frequency(self.pin_y, self.FREQENCY)

        self.pwm.set_servo_pulsewidth(self.pin_x, self.LEVEL_POS_X)
        self.pwm.set_servo_pulsewidth(self.pin_y, self.LEVEL_POS_Y)

    def __del__(self):
        self.cleanup()

    def set_angle(self, pin: int, angle: float):
        if type(angle) != float and type(angle) != int:
            print("Warning: Angle must be a float or int")
            return

        # angle to pulsewidth
        pulsewidth = self.LOW_POS + angle * 10

        # limit cap
        pulsewidth = max(self.LOW_POS, min(self.HIGH_POS, pulsewidth))

        # actuate
        self.pwm.set_servo_pulsewidth(pin, pulsewidth)

    def cleanup(self):
        # os.system("sudo killall pigpiod")
        return


if __name__ == "__main__":
    controller = ServoController()

    servo_x = 17
    servo_y = 18

    angle_x = None
    angle_y = None

    # user input
    while True:
        try:
            angle_y = int(input("Enter angle for servo y: "))
            controller.set_angle(servo_y, angle_y)
        except KeyboardInterrupt:
            print()
            break

    while True:
        try:
            angle_x = int(input("Enter angle for servo x: "))
            controller.set_angle(servo_x, angle_x)
        except KeyboardInterrupt:
            print()
            break

    if angle_x > 180 or angle_x < 0 or angle_y > 180 or angle_y < 0:
        print("Error: Invalid angle")
        exit()

    print("Calibration complete.")
    print("angle_x: ", angle_x)
    print("angle_y: ", angle_y)

    print("Do you want to save these values? (y/N)")
    yn = input().strip()
    if yn in ["y", "Y", "yes", "Yes", "YES"]:
        if not os.path.exists("calibration.txt"):
            with open("calibration.txt", "w") as f:
                f.write(f"{str(angle_x)}, {str(angle_y)}, 100, 100, 0")

        else:
            lines = None
            with open("calibration.txt", "r") as f:
                lines = f.readline().strip().split(", ")
            with open("calibration.txt", "w") as f:
                f.write(
                    f"{str(angle_x)}, {str(angle_y)}, {lines[2]}, {lines[3]}, {lines[4]}"
                )
        print("Saved to calibration.txt")
    else:
        print("Exiting...")
