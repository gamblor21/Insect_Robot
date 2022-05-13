import time
import board
import pwmio
import asyncio
import neopixel
from random import randrange
from adafruit_motor import servo

print("Init")

# create a PWMOut object on Pin A2.
pwm_front = pwmio.PWMOut(board.D7, duty_cycle=2 ** 15, frequency=50)
pwm_back = pwmio.PWMOut(board.D6, duty_cycle=2 ** 15, frequency=50)
pwm_top = pwmio.PWMOut(board.D5, duty_cycle=2 ** 15, frequency=50)
pwm_bottom = pwmio.PWMOut(board.D4, duty_cycle=2 ** 15, frequency=50)

# Create a servo object, my_servo.
front_servo = servo.Servo(pwm_front, min_pulse=500, max_pulse=2500)
back_servo = servo.Servo(pwm_back, min_pulse=500, max_pulse=2650)
top_servo = servo.Servo(pwm_top, min_pulse=500, max_pulse=2500)
bottom_servo = servo.Servo(pwm_bottom, min_pulse=500, max_pulse=2500)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, auto_write=True)

class ServoInfo:
    def __init__(self, servo, angle, step, delay, debug=False):
        self.servo = servo
        self.angle = angle
        self.current_angle = angle
        self.step = step
        self.delay = delay
        self.debug = debug

    def set(self, angle, step, delay):
        if self.angle > angle:
            self.step = -step
        else:
            self.step = step
        self.angle = angle
        self.delay = delay

    @property
    def in_position(self):
        if self.angle == self.current_angle:
            return True
        return False

async def move_servo(servo_info):
    current_angle = servo_info.angle
    while True:
        if current_angle == servo_info.angle:
            await asyncio.sleep(0)
        else:
            current_angle = current_angle + servo_info.step
            try:
                servo_info.servo.angle = current_angle
            except ValueError:
                print("Bad angle: ", current_angle)
            servo_info.current_angle = current_angle
            if servo_info.debug is True:
                print("CA: ", current_angle)
            await asyncio.sleep(servo_info.delay)


async def head_move(top, bottom):
    while True:
        pixel.fill((0,50,0))
        b_angle = randrange(45,135)
        t_angle = randrange(110,160)
        bottom.set(b_angle, 1, 0)
        top.set(t_angle, 1, 0)
        print("Head to ", b_angle, t_angle)
        while bottom.in_position is False or top.in_position is False:
            await asyncio.sleep(0)
        pixel.fill((0,0,50))
        await asyncio.sleep(randrange(1,4))

async def left_step_back(front, back):
    print("Left Back")
    back.set(110, 1, 0.01)
    while back.current_angle < 100:
        await asyncio.sleep(0)
    front.set(110, 1, 0.01)
    while front.current_angle < 100:
        await asyncio.sleep(0)
    back.set(90, 1, 0.01)
    while back.in_position is False:
        await asyncio.sleep(0)

async def right_step_back(front, back):
    print("Right Back")
    back.set(75, 1, 0.01)
    while back.current_angle > 80:
        await asyncio.sleep(0)
    front.set(70, 1, 0.01)
    while front.current_angle > 80:
        await asyncio.sleep(0)
    back.set(90, 1, 0.01)
    while back.in_position is False:
        await asyncio.sleep(0)

async def left_step(front, back):
    print("Left")
    back.set(110, 1, 0.01)
    while back.current_angle < 100:
        await asyncio.sleep(0)
    front.set(70, 1, 0.01)
    while front.current_angle > 70:
        await asyncio.sleep(0)
    back.set(90, 1, 0.01)
    while back.in_position is False:
        await asyncio.sleep(0)

async def right_step(front, back):
    print("Right")
    back.set(75, 1, 0.01)
    while back.current_angle > 80:
        await asyncio.sleep(0)
    front.set(110, 1, 0.01)
    while front.current_angle < 110:
        await asyncio.sleep(0)
    back.set(90, 1, 0.01)
    while back.in_position is False:
        await asyncio.sleep(0)

async def stand(front, back):
    print("Stand")
    front.set(90, 1, 0)
    back.set(90, 1, 0)
    while back.in_position is False or front.in_position is False:
        await asyncio.sleep(0)

async def main():
        pixel.fill((50,0,0))

        front_servo.angle = 90
        front_info = ServoInfo(front_servo, 90, 0, 0)
        front_task = asyncio.create_task(move_servo(front_info))
        time.sleep(0.3)

        pixel.fill((0,0,50))
        back_servo.angle = 90
        back_info = ServoInfo(back_servo, 90, 0, 0, debug=False)
        back_task = asyncio.create_task(move_servo(back_info))
        time.sleep(0.3)

        pixel.fill((50,0,0))
        top_servo.angle = 90
        top_info = ServoInfo(top_servo, 90, 0, 0, debug=False)
        top_task = asyncio.create_task(move_servo(top_info))
        time.sleep(0.3)

        pixel.fill((0,0,50))
        bottom_servo.angle = 90
        bottom_info = ServoInfo(bottom_servo, 90, 0, 0)
        bottom_task = asyncio.create_task(move_servo(bottom_info))

        for _ in range(3):
            await asyncio.sleep(0.5) # let it all swing into start
            pixel.fill((50,0,0))
            await asyncio.sleep(0.5)
            pixel.fill((0,0,0))


        pixel.fill((50,0,0))
        
        print("Starting")

        head_task = asyncio.create_task(head_move(top_info, bottom_info))

        while True:
            await left_step_back(front_info, back_info)
            await right_step_back(front_info, back_info)
            await left_step_back(front_info, back_info)
            await right_step_back(front_info, back_info)

            await stand(front_info, back_info)
            await asyncio.sleep(randrange(1,5))

            await left_step(front_info, back_info)
            await right_step(front_info, back_info)
            await left_step(front_info, back_info)
            await right_step(front_info, back_info)

            await stand(front_info, back_info)
            await asyncio.sleep(randrange(1,5))

        #walk_task = asyncio.create_task(walk(front_info, back_info))

        while True:
            await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main())
