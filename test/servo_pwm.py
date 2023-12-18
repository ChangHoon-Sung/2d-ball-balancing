import RPi.GPIO as GPIO

import time

FREQ = 50  # Hz

LOW_POS = 3  # 3% duty cycle
HIGH_POS = 11  # 11% duty cycle
CENTER_POS = 7  # 7% duty cycle

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

pos_center = CENTER_POS

pwm = GPIO.PWM(18, FREQ)  # (channel, frequency)
pwm.start(pos_center)


def breath_mapping(x):
    x /= 100
    x = 1 - pow(1 - x, 5)
    x = x * (HIGH_POS - LOW_POS) + LOW_POS
    return x


while True:
    try:
        for i in range(100):
            pwm.ChangeDutyCycle(breath_mapping(i))
            time.sleep(0.01)
        for i in range(100, 0, -1):
            pwm.ChangeDutyCycle(breath_mapping(i))
            time.sleep(0.01)
    except ValueError:
        print("Please enter a real number in percent.")

pwm.stop()
GPIO.cleanup()
