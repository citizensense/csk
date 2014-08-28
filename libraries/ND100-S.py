#!/usr/bin/python3
import subprocess

# Class to grab data from a ND100S GPS unit
class ND1000S:

	def grabdata(self):
		output = subprocess.check_output("gpspipe -wn 5 | tail -n 1", shell=True)
		output = output.decode("utf-8")
		output = output.strip()
		return output

if __name__ == "__main__":
	ND = ND1000S()
	print( ND.grabdata() )
