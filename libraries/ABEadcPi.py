#!/usr/bin/python2

from ABElectronics_ADCPi import ADCPi
import time, os, subprocess

# ================================================
# ABElectronics ADC Pi 
# Requires python smbus to be installed
# ================================================

# Retunr a millivolt value of the specified analog input
def readVolts(theinput):
		return adc.readVoltage(theinput)*1000 # return as MilliVolts (mv)
        # return adc.readVoltage(theinput) # Return as Volts (V)

def generateString(ports):
    a1 = '"a1":'+str(readVolts(1))+','
    a2 = '"a2":'+str(readVolts(2))+','
    a3 = '"a3":'+str(readVolts(3))+','
    a4 = '"a4":'+str(readVolts(4))+','
    a5 = '"a5":'+str(readVolts(5))+','
    a6 = '"a6":'+str(readVolts(6))+','
    a7 = '"a7":'+str(readVolts(7))+','
    a8 = '"a8":'+str(readVolts(8))+','
    bus = '"bus":'+ports
    return '{'+a1+a2+a3+a4+a5+a6+a7+a8+bus+'}'

# Initialise the ADC device using the default addresses and sample rate, change this value if you have changed the address selection jumpers
# Sample rate can be 12,14, 16 or 18
try:
    # Set the i2c address (find out what it is with $ i2cdetect -y 1
    adc = ADCPi(0x6a, 0x6b, 16)
    # Print the output in a JSON format
    print(generateString('6a-6b'))
    exit()
except Exception as e:
     pass

# Something strange is happening so lets try
try:
    # Set the i2c address (find out what it is with $ i2cdetect -y 1
    adc = ADCPi(0x69, 0x6b, 16)
    # Print the output in a JSON format
    print(generateString('69-6b'))
    exit()
except Exception as e:
     print('Error: Could not connect to ADC | {}'.format(e))


#try:
#    # Lets check if the adc is avilable on the i2c bus
#    op = subprocess.check_output("i2cdetect -y 1 | grep '69 -- 6b'", shell=True).decode('utf-8')
#    if op.strip() == '':
#        print('I can see the ADC')
#    else:
#        print('Oh dear, the ADC hasn\'t loaded...')
#    print(op)
#except Exception as e:
#    print('Error: Unable to search i2c bus | {}'.format(e))   
