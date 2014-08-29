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

	def resetUSBbus(self):
		on = 'echo 1 > /sys/devices/platform/bcm2708_usb/buspower' 
		off = 'echo 0 > /sys/devices/platform/bcm2708_usb/buspower' 
		subprocess.check_output(off, shell=True).decode("utf-8")
		time.sleep(0.1)
		subprocess.check_output(on, shell=True)
		# Restart the systemd service to allow auto connect of the network
		subprocess.check_output("netctl start eth1static", shell=True)

	def lsusb(self):
		lsusb = subprocess.check_output("lsusb", shell=True).decode("utf-8")
		return lsusb

if __name__ == "__main__":
	LG = LogData()
	

