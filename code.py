import time
import board
import pwmio
import asyncio
import neopixel
from adafruit_motor import servo

print("Init")

# create a PWMOut object on Pin A2.
pwm_front = pwmio.PWMOut(board.D7, duty_cycle=2 ** 15, frequency=50)
pwm_back = pwmio.PWMOut(board.D6, duty_cycle=2 ** 15, frequency=50)

# Create a servo object, my_servo.
front_servo = servo.Servo(pwm_front, min_pulse=500, max_pulse=2500)
back_servo = servo.Servo(pwm_back, min_pulse=500, max_pulse=2500)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=True)

class ServoInfo:
    def __init__(self, servo, angle, step, delay):
        self.servo = servo
        self.angle = angle
        self.step = step
        self.delay = delay

    def set(self, angle, step, delay):
        if self.angle > angle:
            self.step = -step
        else:
            self.step = step
        self.angle = angle
        self.delay = delay

async def move_servo(servo_info):
    current_angle = servo_info.angle
    while True:
        if current_angle == servo_info.angle:
            await asyncio.sleep(0)
        else:
            current_angle = current_angle + servo_info.step
            servo_info.servo.angle = current_angle
            await asyncio.sleep(servo_info.delay)

async def main():
        pixel.fill((100,0,0))

        front_servo.angle = 90
        front_info = ServoInfo(front_servo, 90, 0, 0)
        front_task = asyncio.create_task(move_servo(front_info))

        back_servo.angle = 90
        back_info = ServoInfo(back_servo, 90, 0, 0)
        back_task = asyncio.create_task(move_servo(back_info))

        await asyncio.sleep(1) # let it all swing into start

        while True:
            print("Left")
            pixel.fill((0,100,0))
            front_info.set(65, 1, 0.01)
            await asyncio.sleep(1.0)
            back_info.set(65, 1, 0.01)
            await asyncio.sleep(2.2)

            print("Right")
            pixel.fill((0,0,100))
            front_info.set(115, 1, 0.01)
            await asyncio.sleep(1.0)
            back_info.set(125, 1, 0.01)
            await asyncio.sleep(2.2)

        while True:
            await asyncio.sleep(0)

asyncio.run(main())