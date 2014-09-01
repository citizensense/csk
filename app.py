#!/usr/bin/python3
#############################################################################
# Small application used to Asynchronously: 					   			#
# 	1. Grab sensor data	
#	2. Check status of network and devices
#	2. Save to local csv file					   							#
#	3. Send to server						   								#
#############################################################################
# Include the 'libraries folder' in the system path
import sys, os, time, logging, threading, subprocess, urllib
sys.path.insert(0, '/home/csk/sensorcoms/libraries') #TODO:Make path generic
import wiringpi2
from Huawei3G import *
from ND1000S import *
from SaveData import *
from CherryPyWebServer import CherryPyWebServer

class GrabSensors:
	
	# Initialise the object
	def __init__(self):
		# Setup logging
		logging.basicConfig(filename='csk.log', level=logging.DEBUG)
		self.log('INFO', 'Started script')
		# Setup some base variables
		self.datapath = os.path.join(os.path.dirname(__file__), '../data/data.csv')
		self.csvheader = 'timecode,value1,value2'
		self.ND1000S = ND1000S() 
		self.H3G = Huawei3G()
		self.save = SaveData()
		# Data model
		self.datamodel = {
			'Huawei':"Not connected",
			'ND1000S-LAT':{'title':'lat', 'values':[]},
			'ND1000S-LON':{'title':'lat', 'values':[]},
			'ND1000S-SPEED':{'title':'lat', 'values':[]},
			'ND1000S-ALT':{'title':'lat', 'values':[]},
			'I2C-16ADC-A0':{'title':'lat', 'values':[]},
			'I2C-16ADC-A1-AS-':{'title':'lat', 'values':[]},
			'I2C-16ADC-A2-AS-':{'title':'lat', 'values':[]},
			'I2C-16ADC-A3-AS-':{'title':'lat', 'values':[]},
			'I2C-16ADC-A4-AS-':{'title':'lat', 'values':[]},
			'I2C-16ADC-A5-AS-':{'title':'lat', 'values':[]},
			'I2C-16ADC-A6-AS-':{'title':'lat', 'values':[]},
			'I2C-16ADC-A7-AS-':{'title':'lat', 'values':[]},
			'RPI-WindSpeed':{'title':'lat', 'values':[]},
			'SPI-8ADC--MCP3008-WindDirection':{'title':'lat', 'values':[]},
			'SPI-8ADC-SparkfunSoundDetector-SoundEnv':{'title':'lat', 'values':[]},
			'RPI-SparkfunSoundDetector-SoundGate':{'title':'lat', 'values':[]},
			'I2C-AN2315-Temp':{'title':'lat', 'values':[]},
			'AN2315-Humid':{'title':'lat', 'values':[]},
			'ADC-A7-AS':{'title':'lat', 'values':[]}
		}			
		# Initialise a list of threads so data can be aquired asynchronosly
		threads = []
		threads.append(threading.Thread(target=self.healthcheck) ) # Check device status
		threads.append(threading.Thread(target=self.grabgps) ) # Grab GPS data
		threads.append(threading.Thread(target=self.redled) ) # Blink the LED
		for item in threads:
			item.start()
		# Setup GPOI Pin access
		#wiringpi2.wiringPiSetup() # For sequencial pin numbering i.e [] in pin layout below
		wiringpi2.wiringPiSetupGpio() # For GPIO pin numbering
		# Start the webserver (runs in its own thread)
		globalconfig = {'server.socket_host':"0.0.0.0", 'server.socket_port':80 } 
		localconfig = {'/': {'tools.staticdir.root': '../public'}}
		self.webserver = CherryPyWebServer(globalconfig, localconfig) 
		self.webserver.setcontent('Started the server', 'From within app.py')
	
	# If any threads have new data, then send it here
	def newdata(self, data):
		string = json.encode(self.datamodel)
		# Display the latest data
		self.webserver.setcontent(string, 'From within app.py')
		# Save data to the log file
		self.save.log(self.datapath, self.csvheader, csv)

	# Used for application debugging
	def log(self, level, msg):
		datetime = time.strftime('%d/%m/%Y %H:%M:%S')
		msg = datetime+' '+msg
		if level == 'DEBUG':
			# Print to log 	
			logging.debug(msg)
		elif level == 'INFO':
			# Print to log 
			logging.info(msg)
		elif level == 'WARN':
			# Print to log and console	
			logging.warning(msg)
	
	# Grab GPS data 
	def grabgps(self):
		while True:
			data = self.ND1000S.grabdata()
			try:
				gps=json.loads(data)
				self.log('DEBUG',"GOT GPS: "+data)
				self.newdata(data)
			except ValueError:
				self.log('DEBUG', 'app.py | ValueError | GrabGPS() | '+data)
			time.sleep(6)

	# Thread to check the health of the systemn
	def healthcheck(self):
		while True:
			#self.checklocalserver()
			self.checknetwork()
	
	def checknetwork(self):
		# CHECK NETWORK / 3G DONGLE IS CONNECTED
		network = self.H3G.checkconnection()
		lsusb = self.H3G.lsusb()
		self.log('DEBUG','Checking network connection: '+lsusb)
		if network == "Network OK":
			self.log('DEBUG','Network OK')
			self.datamodel['network'] = 'Huawei Connected'
		else:
			self.log('WARN','USB HAS BEEN reset: Network not connected')
			self.datamodel['network'] = 'Huawei Connected'
		time.sleep(20)

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

