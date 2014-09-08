#!/usr/bin/python3
import os, subprocess, sys, time

# Class to log data capturted by the kit
class SaveData:

	# Accept a full filepath, header and csv: "timestamp, val1", "1234, 77.5"
	def log(self, datafilepath, header, csv):
		# Lets check if the datafile exists
		if not os.path.isfile(datafilepath):
		    # Create the file
		    self.savestring(datafilepath, header)
		csv = csv.strip()
		if len(csv) != 0: 
		    self.savestring(datafilepath, csv)

	# Save a string to a file
	def savestring(self, filepath, string):
		with open(filepath, "a") as text_file:
			print(string, file=text_file)

	# Grab the first #n numer of lines.
	def grabheader(self, fullfilepath, nlines):
		if os.path.exists(fullfilepath):  
			thebytes = subprocess.check_output("head -n1 "+fullfilepath, shell=True)
			return thebytes.decode("utf-8").strip()
		else:
			return 'no file found at: '+fullfilepath

# Example showing how to to use this class
if __name__ == "__main__":
	# Setup elements for this example
	import os, random
	save = SaveData()
	# Generate vars
	datafilepath = os.path.join(os.path.dirname(__file__), '../data/data.csv')
	webfilepath = os.path.join(os.path.dirname(__file__), '../public/latest.txt')
	header = 'timecode,value1,value2'
	time = str(random.randint(2000,50000))
	val1 = str(random.uniform(1, 65000))
	val2 = str(random.uniform(1, 65000))
	csv = time+','+val1+','+val2
	# Log the data
	save.log(datafilepath, header, csv)

