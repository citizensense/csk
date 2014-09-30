#!/usr//bin/python3
import wiringpi2 as wiringpi
from time import sleep
wiringpi.wiringPiSetupGpio
pin = 17
wiringpi.pinMode(pin, 1)

while True:
    wiringpi.digitalWrite(pin, 0)
    sleep(0.5)
    wiringpi.digitalWrite(pin, 1)
    sleep(0.5)

