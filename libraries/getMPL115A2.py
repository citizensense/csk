#!/usr/bin/python2

import time, signal, sys
from Adafruit_ADS1x15 import ADS1x15

ADS1115 = 0x01	# 16-bit ADC # 0x00 12-bit ADC

# Select the gain
#gain = 6144  # +/- 6.144V
# gain = 4096  # +/- 4.096V 
# gain = 2048  # +/- 2.048V
# gain = 1024  # +/- 1.024V
gain = 512   # +/- 0.512V
#gain = 256   # +/- 0.256V

# Select the sample rate
sps = 8    # 8 samples per second
# sps = 16   # 16 samples per second
# sps = 32   # 32 samples per second
# sps = 64   # 64 samples per second
# sps = 128  # 128 samples per second
# sps = 250  # 250 samples per second
# sps = 475  # 475 samples per second
# sps = 860  # 860 samples per second

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1x15(ic=ADS1115)

# Read channel 0 in single-ended mode using the settings above
a0 = adc.readADCSingleEnded(0, gain, sps)
a1 = adc.readADCSingleEnded(1, gain, sps)
a2 = adc.readADCSingleEnded(2, gain, sps)
a3 = adc.readADCSingleEnded(3, gain, sps)

# To read channel 3 in single-ended mode, +/- 1.024V, 860 sps use:
# volts = adc.readADCSingleEnded(3, 1024, 860)
print "A0:WE2,A1:WE3,A2:(pot)AE3,A3:PT+"
print "{0},{1},{2},{3}".format(a0, a1, a2, a3)

#========CONNECTIONS:AEF->Adafruit 16-bit ADC
# 
# PT+ -> A3
# AE3 -> A2
# WE3 -> A1 
# WE2 -> A0
#
#=====PIN LAYOUT OF AEF BOARD===============
#
#  PIDVIN +6v WE1 WE2 WE3 PT+
#     ------------------------
#     |__|___|___|___|___|___|
#	  |__|___|___|___|___|___|
# PIDVOUT GND AE1 AE2 AE3 PT-
#
#======16BIT ADC PINS=======================
# 
# VDD GND SCL SDA ADDR ALRT A0 A1 A2 A3 
#
#===========================================



