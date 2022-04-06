#ADVERTISER 1

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
advertisement = AdafruitColor()
color = 0x110000 #0x110000 for advertiser 1, 0x000011 for advertiser 2
advertisement.color = color

async def blink(pin, interval, count):
    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output(value=False)
        for _ in range(count):
            led.value = True
            await asyncio.sleep(interval)
            led.value = False
            await asyncio.sleep(interval)

async def buzz(pin, frequency, duration, interval, count):
    for f in (262, 294, 330): #(262, 294, 330) for advertiser 1, (349, 392, 440) for advertiser 2
        simpleio.tone(board.A2, f, duration)
        await asyncio.sleep(interval) #tab left to have the tone finish together before moving onto led

async def main():
    led_task = asyncio.create_task(blink(board.D13, 0.1, 1)) #0.1 interval for advertiser 1, 0.5 interval for advertiser 2
    piezo_task = asyncio.create_task(buzz(board.A2, 330, 0.25, 0.1, 1)) #0.1 interval for advertiser 1, 0.5 interval for advertiser 2
    await asyncio.gather(led_task, piezo_task)
    print("Done")

while True:
    print("Broadcasting color")
    ble.start_advertising(advertisement)
    advertisement.color = color
    print("Color: {:06x}".format(color))
    while True:
        asyncio.run(main())
        ble.stop_advertising()
        ble.start_advertising(advertisement)
        time.sleep(0.1)
ble.stop_advertising()
