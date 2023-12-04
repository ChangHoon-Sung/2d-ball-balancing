import time
from typing import Tuple

import RPi.GPIO as GPIO


class PDController:
    def __init__(self, kp_x: float, kd_x: float, kp_y: float, kd_y: float):
        self.kp_x: float = kp_x
        self.kd_x: float = kd_x
        self.kp_y: float = kp_y
        self.kd_y: float = kd_y
        self.desired_position: Tuple[float, float] = (None, None)
        self.current_position: Tuple[float, float] = (None, None)
        self.previous_error: Tuple[float, float] = (None, None)
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

        self.output = (
            self.kp_x * error_x + self.kd_x * derivative_x,
            self.kp_y * error_y + self.kd_y * derivative_y,
        )
        self.previous_error = (error_x, error_y)

    def get_output(self) -> Tuple[float, float]:
        return self.output


class ServoController:
    def __init__(self, pin_x: int = 17, pin_y: int = 18):
        self.FREQENCY = 50      # Hz
        self.LOW_POS = 3        # 3% duty cycle
        self.LEVEL_POS_X = 7    # 7% duty cycle
        self.LEVEL_POS_Y = 7    # 7% duty cycle
        self.HIGH_POS = 11      # 11% duty cycle

        self.pin_x = pin_x
        self.pin_y = pin_y

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin_x, GPIO.OUT)
        GPIO.setup(self.pin_y, GPIO.OUT)

        self.pwm_x = GPIO.PWM(self.pin_x, self.FREQENCY)
        self.pwm_y = GPIO.PWM(self.pin_y, self.FREQENCY)

        self.pwm_x.start(self.LEVEL_POS_X)
        self.pwm_y.start(self.LEVEL_POS_Y)

    def set_angle(self, angle_x: float, angle_y: float):
        duty_x = angle_x / 18 + 2
        duty_y = angle_y / 18 + 2

        duty_x = max(self.LOW_POS, min(self.HIGH_POS, duty_x))
        duty_y = max(self.LOW_POS, min(self.HIGH_POS, duty_y))
        
        self.pwm_x.ChangeDutyCycle(duty_x)
        self.pwm_y.ChangeDutyCycle(duty_y)

    def cleanup(self):
        GPIO.cleanup()
