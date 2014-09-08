#!/usr/bin/python3
import subprocess, logging, sys, time

# Class to grab data from a ND100S GPS unit
class Huawei3G:

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
		#time.sleep(0.1)
		#subprocess.check_output(on, shell=True)
		# Restart the systemd service to allow auto connect of the network
		#subprocess.check_output("netctl start eth1static", shell=True)

	def lsusb(self):
		lsusb = subprocess.check_output("lsusb", shell=True).decode("utf-8")
		return lsusb

if __name__ == "__main__":
	h3g = Huawei3G()
	print( h3g.lsusb )
	print( h3g.checkconnection() )

# Example output
#Bus 001 Device 024: ID 12d1:14db Huawei Technologies Co., Ltd. E353/E3131
#Bus 001 Device 005: ID 046d:c52b Logitech, Inc. Unifying Receiver
#Bus 001 Device 004: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
#Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
#Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. SMC9514 Hub
#Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub 
