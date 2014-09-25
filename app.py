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
from collections import OrderedDict
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, 'libraries') ) 
#import wiringpi2
from datetime import datetime
from Huawei3G import *
from ND1000S import *
from SaveData import *
from CherryPyWebServer import CherryPyWebServer
from Alphasense import *

class GrabSensors:
	
	# Initialise the object
	def __init__(self):
		# Setup logging
		logging.basicConfig(filename='csk.log', level=logging.DEBUG)
		self.log('INFO', 'Started script')
		# Setup some base variables
		self.lock = threading.Lock()
		self.datapath = os.path.join(os.path.dirname(__file__), 'data/data.csv')
		self.ND1000S = ND1000S() 
		self.H3G = Huawei3G()
		self.save = SaveData()
		# Setup Alphasense calibration
		weSN1 = 310     # VpcbWE-SN1-zero 
		weSN2 = 412     # VpcbWE-SN2-zero
		weSN3 = 280     # VpcbWE-SN3-zero
		aeSN1 = 312     # VpcbAE-SN1-zero
		aeSN2 = 413     # VpcbAE-SN2-zero
		aeSN3 = 270     # VpcbAE-SN3-zero
		SN1sensi = 0.54     # "Sensitivity (mV/ppb)"
		SN2sensi = 0.238    # "Sensitivity (mV/ppb)"
		SN3sensi = 0.362    # "Sensitivity (mV/ppb)"
		self.alphasense = Alphasense(weSN1, weSN2, weSN3, aeSN1, aeSN2, aeSN3, SN1sensi, SN2sensi, SN3sensi)
		# Start the webserver (runs in its own thread)
		globalconfig = {'server.socket_host':"0.0.0.0", 'server.socket_port':80 } 
		localconfig = {'/': {'tools.staticdir.root': '../public'}}
		self.webserver = CherryPyWebServer(globalconfig, localconfig) 
		self.webserver.setcontent('Started the server', 'From within app.py')
		# Data model: (shortname, [logtitle, values, max, min])
		self.datamodel = OrderedDict([
			('lat',				['USB-ND1000S', 	[]	]),
			('lon',				['ND1000S-LON', 	[]	]),
			('groundspeed', 	['ND1000S-SPEED', 	[]	]),
			('altitude',		['ND1000S-ALT',		[]	]),
			('PID',				['A1->16ADC->I2C',	[]	]),
			('SO2 A4 [WE3]',	['A2->16ADC->I2C',	[]	]),
			('SO2 A4 [AE3]',	['A3->16ADC->I2C',	[]	]),
			('O3 A4 [WE2]',		['A4->16ADC->I2C',	[]	]),
			('O3 A4 [AE2]',		['A5->16ADC->I2C',	[]	]),
			('NO2 A4 [WE1]',	['A6->16ADC->I2C',	[]	]),
			('NO2 A4 [AE1]',	['A7->16ADC->I2C',	[]	]),
			('TEMP [PT+]',		['A8->16ADC->I2C',	[]	]),
			('TEMP [PT+]',		['A8->16ADC->I2C',	[]	]),
            ('SO2ppb',		    ['',	[]	]),
            ('O3ppb',		    ['',	[]	]),
            ('NO2ppb',		    ['',	[]	]),
            ("Temp'C",		    ['',	[]	]),
			('spec',			['A8->16ADC->I2C',	[]	]),
			('spechumid',		['??/',				[]	]),
			('windspeed',		['RPI-WindSpeed',	[]	]),
			('winddir',			['SPI-8ADC--MCP3008-WindDirection',			[]	]),
			('soundenv',		['SPI-8ADC-SparkfunSoundDetector-SoundEnv',	[]	]),
			('soundgate',		['RPI-SparkfunSoundDetector-SoundGate',		[]	]),
			('outsidetemp',		['I2C-AN2315-Temp',	[]	]),
			('outsidehumid',['AN2315-Humid',	[]	]),
			('rpiTempC',	['RPi-TempC',		[]	]),
			('rpi%diskused',['RPi-disk % used',	[]	]),
			('rpidiskavail',['RPi-diskAvail',	[]	]),
			('rpiload',		['Rpi-CPU Load Ave',[]	]),
			('networkup',	['HuaweiAvailable', []	])
		])
		# Place to store asychronosly generated values
		self.csvbuffer = OrderedDict([])
		# Initialise a list of threads so data can be aquired asynchronosly
		threads = []
		threads.append(threading.Thread(target=self.healthcheck) ) 	# Check device status
		threads.append(threading.Thread(target=self.grabgps) ) 		# Grab GPS data
		threads.append(threading.Thread(target=self.grabrpiinfo) ) 	# Grab RaspberryPi Info
		threads.append(threading.Thread(target=self.savedata) ) 	# Save Data to webGUI, LogFile
		threads.append(threading.Thread(target=self.grabadc) ) 		# Grab data from ADC 
		for item in threads:
			item.start()
		# Setup GPOI Pin access
		#wiringpi2.wiringPiSetup() # For sequencial pin numbering i.e [] in pin layout below
		#wiringpi2.wiringPiSetupGpio() # For GPIO pin numbering
	
	# If any threads have new data, then send it here
	def newdata(self, key, value):
		# Create a timecode
		timecode = int(time.time())
		# TODO: Need to check the Rpi has the right time, otherwise we shouldn't save
		# Create a lock so multiple threads don't get confused
		self.lock.acquire()
		try:
			keyindex = list(self.datamodel.keys()).index(key)
			# Create a buffer with n list locations to store this data if needed
			if timecode not in self.csvbuffer: 
				self.csvbuffer[timecode] = [""]*len(self.datamodel)
			# Save to our csv buffer, ready for saving to the log
			self.csvbuffer[timecode][keyindex] = ""+str(value)
			# save the last n values to our model
			if len(self.datamodel[key][1]) > 4:
				self.datamodel[key][1].pop(0)
			self.datamodel[key][1].append([timecode, value])
		# Release the lock
		finally:
			self.lock.release()
    
    # Iterate through the data model and save data to: LogFile, GUI, Web
	def savedata(self):
		while True:
			# Block if the lock is already held by another process
			self.lock.acquire() 
			try:
				# Prep  web interface output
				thistime = time.strftime("%d/%m/%Y %H:%M:%S")
				mystr = ""
				header = "timestamp, humandate"
				hs = ''
				for key in self.datamodel:
					values = ""
					header = header+hs+key
					for value in self.datamodel[key][1]: 
						timecode = str(value[0]) 
						val = str(value[1])
						values = val+', '+values
					mystr += '<div><b>'+key+':</b> '+values+'</div>'
					hs = ', '
				# Prep the CSV output
				csvbuffer = ""
				for timecode in self.csvbuffer:
				    ht = datetime.fromtimestamp( timecode ).strftime('%Y-%m-%d %H:%M:%S')
				    csvbuffer = csvbuffer+str(timecode)+','+ht+','.join(self.csvbuffer[timecode])+"\n"
				# Export to the web interface
				self.webserver.setcontent('<h2>'+thistime+'</h2><pre>'+mystr+'</pre>', header+'<hr /><pre>'+csvbuffer+'</pre>')
				# Save data to the log file
				# TODO: Check the string isn't empty!!
				self.save.log(self.datapath, header, csvbuffer)
				# Now TODO: if the data has been saved, clear the buffer
				self.csvbuffer = OrderedDict([])
			finally:
				self.lock.release()
			time.sleep(5)

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
				info=json.loads(data)
				self.log('DEBUG',"GOT GPS: "+data)
				self.newdata('lat', info["lat"] )
				self.newdata('lon', info["lon"] )
				self.newdata('groundspeed', info["speed"] )
				self.newdata('altitude', info["alt"] )
			except ValueError:
				self.log('DEBUG', 'app.py | ValueError | GrabGPS() | '+data)
			time.sleep(6)
	
	# Grab ADC data from the ABelectronicsADC
	def grabadc(self):
		while True: 
			jsonstr = subprocess.check_output("python2 libraries/ABEadcPi.py", shell=True).decode("utf-8")
			try:
				info=json.loads(jsonstr)
				self.log('DEBUG',"Got ADC Info"+jsonstr)
				self.newdata('PID', info["a1"] ) 
				self.newdata('SO2 A4 [WE3]', info["a3"] )
				self.newdata('SO2 A4 [AE3]', info["a2"] )
				self.newdata('O3 A4 [WE2]', info["a5"] )
				self.newdata('O3 A4 [AE2]', info["a4"] )
				self.newdata('NO2 A4 [WE1]', info["a7"] )
				self.newdata('NO2 A4 [AE1]', info["a6"] )
				self.newdata('TEMP [PT+]', info["a8"] )
				temp = 23
				print(jsonstr)
				# sensor, ae, we, temp 
				SO2 = self.alphasense.readppb('SO2a4', info['a3'], info['a2'], temp) 
				O3 = self.alphasense.readppb('O3a4', info['a5'], info['a4'], temp)
				NO2 = self.alphasense.readppb('NO2a4', info['a7'], info['a6'], temp)  
				print('APP NO2: '+str(NO2)+"-------\n")
				self.newdata('SO2ppb', SO2 )
				self.newdata('O3ppb', O3 )
				self.newdata('NO2ppb', NO2 )
				self.newdata("Temp'C", 23)
			except ValueError:
				self.log('DEBUG', 'app.py | JsonError | grabadc() | '+jsonstr)
			time.sleep(3)

	# Grab RpiInfo
	def grabrpiinfo(self):
		while True: 
			jsonstr = subprocess.check_output("libraries/RPiInfo.sh", shell=True).decode("utf-8")
			try:
				info=json.loads(jsonstr)
				self.log('DEBUG',"Got RaspberryPi Info"+jsonstr)
				self.newdata('rpiTempC', info["tempc"] ) 
				self.newdata('rpi%diskused', info["disk%used"] )
				self.newdata('rpidiskavail', info["diskavailable"] )
				self.newdata('rpiload', info["load"] )
				#self.newdata(tc, 'deviceinfo', info["serial"] )
			except ValueError:
				self.log('DEBUG', 'app.py | ValueError | GrabGPS() | '+jsonstr)
			time.sleep(20)

	# Thread to check the health of the systemn
	def healthcheck(self):
		while True:
			self.checknetwork()
	
	def checknetwork(self):
		# CHECK NETWORK / 3G DONGLE IS CONNECTED
		network = self.H3G.checkconnection()
		lsusb = self.H3G.lsusb()
		self.log('DEBUG','Checking network connection: '+lsusb)
		if network == "Network OK":
			self.log('DEBUG','Network OK')
			self.newdata('networkup', 1)
		else:
			self.log('WARN','USB HAS BEEN reset: Network not connected')
			self.newdata('networkup', 0)
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

