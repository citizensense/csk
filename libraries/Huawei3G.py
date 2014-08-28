#!/usr/bin/python3
import subprocess, sys

# Class to grab data from a ND100S GPS unit
class Huawei3G:

	# Lets start things up
	def __init__(self):
		self.checkconnection()

	def checkconnection(self):
		output = ""
		output = subprocess.check_output("lsusb", shell=True).decode("utf-8")
		devicepresent = output.find("Huawei")
		if devicepresent > -1:
			msg = output+"3G Device found! Checking it's in the correct mode... \n"
			mode = output.find("(Mass storage mode)")
			if mode > -1:
				msg = msg+"3G Device In Mass Storage Mode"
		else:
			msg = output+"3G Device Not Found"
		print(msg)

	def resetUSBbusPower(self):
		subprocess.check_output("lsusb", shell=True).decode("utf-8")

if __name__ == "__main__":
	Huawei3G()

#Bus 001 Device 024: ID 12d1:14db Huawei Technologies Co., Ltd. E353/E3131
#Bus 001 Device 005: ID 046d:c52b Logitech, Inc. Unifying Receiver
#Bus 001 Device 004: ID 067b:2303 Prolific Technology, Inc. PL2303 Serial Port
#Bus 001 Device 003: ID 0424:ec00 Standard Microsystems Corp. SMSC9512/9514 Fast Ethernet Adapter
#Bus 001 Device 002: ID 0424:9514 Standard Microsystems Corp. SMC9514 Hub
#Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
#3G Device found! 

