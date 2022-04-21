#DEVICE #

import time
import board
import digitalio
import simpleio
import pwmio

import neopixel

from digitalio import DigitalInOut, Direction, Pull
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

#note frequencies (slight differences amongst each device for producing dissonance)
C4 = 262
D4 = 294
E4 = 330
F4 = 349
G4 = 392
A4 = 440
B4 = 494

#note array
note_options = [C4, D4, E4, F4, G4, A4, B4]

#colors for neopixel
color_C = 0x110000
color_D = 0x111100
color_E = 0x001100
color_F = 0x001111
color_G = 0x000011
color_A = 0x110011
color_B = 0x111111

#color array
color_options = [color_C, color_D, color_E, color_F, color_G, color_A, color_B]

#scanner dictionary
play_note = {"1114112":262, "1118464":294, "4352": 330, "4369": 349, "17": 392, "1114129": 440, "1118481": 494}

#setup BLE connection
ble = BLERadio()

slide_switch = DigitalInOut(board.D11)
slide_switch.pull = Pull.DOWN #UP for advertise, DOWN for scan - need to add a slide switch
button = DigitalInOut(board.A4)
button.direction = Direction.INPUT
button.pull = Pull.UP

neopixels = neopixel.NeoPixel(board.NEOPIXEL, 1)

buzzer = pwmio.PWMOut(board.A2, variable_frequency=True)

i = 0
advertisement = AdafruitColor()
advertisement.color = color_options[i]
neopixels.fill(color_options[i])

#buzzer duty cycle states
ON = 2**15
OFF = 0

buzzer.frequency = note_options[i]
buzzer.duty_cycle = ON

while True:
    #the first mode is the advertiser broadcasts it's current color and tone to other devices.
    if slide_switch.value:
        print("Broadcasting color and tone")
        ble.start_advertising(advertisement)
        while slide_switch.value:
            last_i = i
            if not button.value:
                print("Button pressed")
                i += 1
            i %= len(color_options)
            if last_i != i:
                color = color_options[i]
                print("New color {:06x}".format(color))
                buzzer.frequency = note_options[i]
                print(buzzer.frequency)
                advertisement.color = color
                ble.stop_advertising()
                ble.start_advertising(advertisement)
                time.sleep(0.5)
        ble.stop_advertising()

    #the second mode scans for color broadcasts and shows the color and tone of the strongest signal.
    else:
        closest = None
        closest_rssi = -80
        closest_last_time = 0
        #print("Scanning for colors")
        while not slide_switch.value:
            for entry in ble.start_scan(AdafruitColor, minimum_rssi=-100, timeout=1):
                if slide_switch.value:
                    break
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
                neopixels.fill(0x000000)
                print(entry.color)
                color_options[i] = entry.color
                neopixels.fill(color_options[i])
                note = str(entry.color)
                print(str(play_note[note]))
                buzzer.duty_cycle = ON
                buzzer.frequency = play_note[note]

            #clear the pixels if we haven't heard from anything recently.\
            now = time.monotonic()
            if now - closest_last_time > 1:
                neopixels.fill(0x000000)
                neopixels.show()
                buzzer.duty_cycle = OFF
        ble.stop_scan()
