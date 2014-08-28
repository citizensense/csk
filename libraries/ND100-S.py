#!/usr/bin/python3
import subprocess

# Class to grab data from a ND100S GPS unit
class ND1000S:

	# Lets start things up
	def __init__(self):
		self.grabdata()

	def grabdata(self):
		output = subprocess.check_output("gpspipe -wn 5 | tail -n 1", shell=True)
		output.decode("utf-8")
		output = output.strip()
		print(output)

if __name__ == "__main__":
	ND1000S()
