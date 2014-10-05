#!/usr/bin/python3
import subprocess, json

# Class to grab data from a ND100S GPS unit
class ND1000S:

    def __init__(self):
        self.msg = ''

	def grabdata(self):
	    self.msg = '=====GPS==grabdata()======'
	    try:
		    output = subprocess.check_output("gpspipe -wn 5 | tail -n 1", shell=True)
		    output = output.decode("utf-8")
		    output = output.strip()
		    foundlat = output.find('"alt":')
		except Exception as e:
		    return False
		if foundlat > -1:
			# Found some data, lets return it as valid json
			try:
				gps=json.loads(output)
				op = '{'
				op += '"lat":"'+str(gps['lat'])+'",'
				op += '"lon":"'+str(gps['lon'])+'",'
				op += '"time":"'+str(gps['time'])+'",'
				op += '"alt":"'+str(gps['alt'])+'",'
				op += '"speed":"'+str(gps['speed'])+'"'
				op += '}'
				return op
			except ValueError:
				return "INVALID GPS JSON: "+output
			return output
		else:
			return "NO GPS FOUND: "+output

if __name__ == "__main__":
	ND = ND1000S()
	print( ND.grabdata() )
