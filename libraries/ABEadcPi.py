#!/usr/bin/python2

from ABElectronics_ADCPi import ADCPi
import time
import os

# ================================================
# ABElectronics ADC Pi ACS712 30 Amp current sensor demo
# Version 1.0 Created 15/07/2014
#
# Requires python smbus to be installed
# run with: python demo-acs712-30.py
# ================================================


# Initialise the ADC device using the default addresses and sample rate, change this value if you have changed the address selection jumpers
# Sample rate can be 12,14, 16 or 18
adc = ADCPi(0x68, 0x69, 12)

# change the 2.5 value to be half of the supply voltage.

def calcCurrent(inval):
		return ((inval) - 2.5) / 0.066;

a1 = '"a1":'+str(adc.readVoltage(1))+','
a2 = '"a2":'+str(adc.readVoltage(2))+','
a3 = '"a3":'+str(adc.readVoltage(3))+','
a4 = '"a4":'+str(adc.readVoltage(4))+','
a5 = '"a5":'+str(adc.readVoltage(5))+','
a6 = '"a6":'+str(adc.readVoltage(6))+','
a7 = '"a7":'+str(adc.readVoltage(7))+','
a8 = '"a8":'+str(adc.readVoltage(8))

print('{'+a1+a2+a3+a4+a5+a6+a7+a8+'}')
