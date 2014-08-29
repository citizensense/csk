#!/usr/bin/python3
import subprocess, sys, time

# Class to log data capturted by the kit
class LogData:
	
	def __init__(self):
		# First check we have a data file to save to, if not, create it

	def checkconnection(self):
		ipa = subprocess.check_output("ip a", shell=True).decode("utf-8")
		network = ipa.find("eth1")
		# If eth1 isnt found then restart the usb bus
		if network == -1:
			self.resetUSBbus()
			return "No network present on Eth1. Restart USB bus"
		else:
			return "Network OK"

	# Grab the first #n numer of lines.
    def grabheader(self, fullfilepath, nlines):
        if os.path.exists(fullfilepath):  
            thebytes = subprocess.check_output("head -n1 "+fullfilepath, shell=True)
            return thebytes.decode("utf-8").strip()
        else:
            return 'no file found at: '+fullfilepath




if __name__ == "__main__":
	LG = LogData()
	

