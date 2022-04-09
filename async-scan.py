#SCANNER #

import time
import board
import digitalio
import asyncio
import simpleio

from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

# Setup BLE connection
ble = BLERadio()

#advertiser 1 pattern
async def blink(pin, interval, count):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            led.value = True
            await asyncio.sleep(interval)
            led.value = False
            await asyncio.sleep(interval)

async def buzz(pin, frequency, duration, interval, count):
    for _ in range(count):
        for f in (262, 294, 330):
            simpleio.tone(board.A2, f, duration)
            await asyncio.sleep(interval) #tab left to have the tone finish together before moving onto led

async def main_1():
    led_task = asyncio.create_task(blink(board.D13, 0.1, 1))
    piezo_task = asyncio.create_task(buzz(board.A2, 262, 0.25, 0.1, 1))
    await asyncio.gather(led_task, piezo_task)
    print("Pattern 1: Done")

#advertiser 2 pattern
async def blink(pin, interval, count): #blink the given pin forever.
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            led.value = True
            await asyncio.sleep(interval)
            led.value = False
            await asyncio.sleep(interval)

async def buzz(pin, frequency, duration, interval, count): #buzz the given pin forever
    for _ in range(count):
        for f in (349, 392, 440):
            simpleio.tone(board.A2, f, duration)
            await asyncio.sleep(interval) #tab left to have the tone finish together before moving onto led

async def main_2():
    led_task = asyncio.create_task(blink(board.D13, 0.5, 1))
    piezo_task = asyncio.create_task(buzz(board.A2, 349, 0.25, 0.5, 1))
    await asyncio.gather(led_task, piezo_task) # This will run forever, because neither task ever exits.
    print("Pattern 2: Done")

while True:
    closest = None
    closest_rssi = -80
    closest_last_time = 0
    print("Scanning for colors")
    while True:
        for entry in ble.start_scan(AdafruitColor, minimum_rssi=-100, timeout=1):
            now = time.monotonic()
            new = False
            if entry.address == closest:
                pass
            elif entry.rssi > closest_rssi or now - closest_last_time > 0.4:
                closest = entry.address
            else:
                continue
            closest_rssi = entry.rssi
            closest_last_time = now
            print(entry.rssi)
            print("Color {:06x}".format(entry.color))
        if entry.color == 0x110000: #advertiser 1
            asyncio.run(main_1())
        elif entry.color == 0x000011: #advertiser 2
            asyncio.run(main_2())
        else:
            ble.stop_scan()
