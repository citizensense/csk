#!/usr/bin/python3
#############################################################################
# Small application used to Asynchronously: 					   			#
# 	1. Grab sensor data	
#	2. Check status of network and devices
#	2. Save to local csv file					   							#
#	3. Send to server						   								#
#############################################################################
# Include the 'libraries folder' in the system path
import sys, os, time, threading, subprocess, urllib
sys.path.insert(0, '/home/csk/sensorcoms/libraries') #TODO:Make generic
import wiringpi2
#from Adafruit_MPL115A2 import *
from Huawei3G import *
from ND1000S import *

class GrabSensors:
	
	# Initialise the object
	def __init__(self):
		# Setup some base varibles
		self.ND1000S = DN1000S() 
		self.H3G = Huawei3G()
		self.status = {'devices':{'Huawei':{'status':'0','msg':'Unchecked'}}}
		self.data = {}
		self.startlocalserver()
		# Initialise a list of threads so data can be aquired asynchronosly
		threads = []
		threads.append(threading.Thread(target=self.healthcheck) ) # Check device status
		threads.append(threading.Thread(target=self.grabgps) ) # Grab GPS data
		#threads.append(threading.Thread(target=self.barom) ) # Start baromerter thread
		threads.append(threading.Thread(target=self.redled) ) # Blink the LED
		for item in threads:
			item.start()
		# Setup GPOI Pin access
		#wiringpi2.wiringPiSetup() # For sequencial pin numbering i.e [] in pin layout below
		wiringpi2.wiringPiSetupGpio() # For GPIO pin numbering
	
	def grabgps(self){
		while True:
			data = self.ND1000S.grabdata()
			print(data)
	}

	# Thread to check the health of the systemn
	def healthcheck(self):
		while True:
			#self.checklocalserver()
			self.checknetwork()
	
	def checklocalserver(self):
		print('Chec')

	def checknetwork(self):
		# CHECK NETWORK / 3G DONGLE IS CONNECTED
		network = self.H3G.checkconnection()
		lsusb = self.H3G.lsusb()
		#print(network+'\n'+lsusb)
		if network != "":
			self.status['devices']['Huawei']['status'] = 1
			self.status['devices']['Huawei']['msg'] = 'Connected'
		else:
			self.status['devices']['Huawei']['status'] = 0
			self.status['devices']['Huawei']['msg'] = 'Not Connected'
		time.sleep(20)
	
	def startlocalserver(self):
		# Start an ultra minimal local server	
		cmd = "cd /home/csk/sensorcoms/public;python -m http.server 80 > /dev/null 2>&1"

	# Thread to blink an led
	def redled(self):
		gpiopin=23
		onoff=0
		wiringpi2.pinMode(gpiopin,1) 		# Set pin to 1 ( OUTPUT )
		wiringpi2.digitalWrite(gpiopin,1) 	# Write 1 ( HIGH ) to pin 
		#wiringpi2.digitalRead(pin)  		# Read pin 
		while True:
			time.sleep(0.25)
			onoff = not onoff
			wiringpi2.digitalWrite(gpiopin,onoff) # Write 1 ( HIGH ) to pin 

	# Thread to grab Barometer/Temp data from a: MPL115A2
	def barom(self):	
		while True:
			# read coefficients
			i2c.write(0x60, 0x00)
			print("a0_MSB:"+str( i2c.read(dev1) ) )
			#i2c.write(0x60, 0x00)
			#print('i2cX60: '+str( i2c.read(dev2) ) )
			time.sleep(2)
	
# Start grabbing sensors
GrabSensors()

##############################################################################
# RaspberryPi Pin Layout													 #
# TODO: Checkout alt pin numbering: http://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python
#============================================================================#
#        _____            ________											 #
#        | pwr |          | SDcard |          								 #
# 	 ---------------------------------										 #
#	 | 	   		    	3v3 [ 1][ 2] | 5v									 #		 
#	 |   	 GPIO0/SDA0-I2c [ 3][ 4] | 5v									 #		
#	 |   	 GPIO1/SCL0-I2c [ 5][ 6] | GND									 #
#	 |  		 	 GPCLK0 [ 7][ 8] | GPIO14/UART0-TXD						 #
#	 | 	  			    GND [ 9][10] | GPIO15/UART0-RXD						 #
#	 |  		 	 GPIO17 [11][12] | GPIO18/PCM_CLK   					 #
#	 |  		 	 GPIO21 [13][14] | GND									 #
#	 |  		 	 GPIO22 [15][16] | GPIO23								 #
#	 |	  		    	3v3 [17][18] | GPIO24								 #
#	 | 	   GPIO10/SPIO_MOSI [19][20] | GND									 #
#	 |  	GPIO9/SPIO_MISO [21][22] | GPIO25								 #
#	 | 	   GPIO11/SPIO_SCLK [23][24] | GPIO8/SPIO_CE0_N						 #
#	 |	 	 	    	GND [25][26] | GPIO7/SPIO_CE1_N						 #
# hdmi								 |___									 #
#	 |								 |vid|									 #
#	 |                               |---									 #
#	 |								 |___								     #
#	 |								 |aud|									 #
# 	 |								 |---									 #
#	 |								 |										 #
# 	 ---------------------------------										 #
#      | eth |  | usb |														 #
#      -------  -------														 #
# 																			 #
##############################################################################

