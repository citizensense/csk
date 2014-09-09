#!/usr/bin/python2

from ABElectronics_ADCPi import ADCPi
import time
import os

# ================================================
# ABElectronics ADC Pi 
# Requires python smbus to be installed
# ================================================

# Retunr a millivolt value of the specified analog input
def readVolts(theinput):
		# return adc.readVoltage(theinput)*1000 # return as MilliVolts (mv)
        return adc.readVoltage(theinput) # Return as Volts (V)

def generateString():
    a1 = '"a1":'+str(readVolts(1))+','
    a2 = '"a2":'+str(readVolts(2))+','
    a3 = '"a3":'+str(readVolts(3))+','
    a4 = '"a4":'+str(readVolts(4))+','
    a5 = '"a5":'+str(readVolts(5))+','
    a6 = '"a6":'+str(readVolts(6))+','
    a7 = '"a7":'+str(readVolts(7))+','
    a8 = '"a8":'+str(readVolts(8))
    return '{'+a1+a2+a3+a4+a5+a6+a7+a8+'}'

# Initialise the ADC device using the default addresses and sample rate, change this value if you have changed the address selection jumpers
# Sample rate can be 12,14, 16 or 18
try:
    adc = ADCPi(0x6a, 0x6b, 16)
    # Print the output in a JSON format
    print(generateString())
except:
    print('Error: Could not connect to ADC')

