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
            if output == '':
                self.msg += "\ngps: No gpsd software is running"
                self.startgpsd()
                return False
            else:
                foundlat = output.find('"alt":')
                self.msg += "\ngps: gpsd application is running"
        except Exception as e:
            self.msg += "\ngps: Error: {}".format(e)
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
                self.msg += "\ngps: Found data"
                return op
            except Exception as e:
                self.msg += '\ngps: Couldn\'t load gps json:'.format(e)
                return False 
            return output
        else:
            self.msg += '\ngps: Couldn\'t find coordinates. Possibly waiting for a fix.'
            return False

    # Startup GPS software
    def startgpsd(self):
        try:
            output = subprocess.check_output("gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock &", shell=True)
            self.msg += '\ngps: Starting gpsd application'
        except Exception as e:
            self.msg += '\ngps: Enable to start gpsd application. Error: {}'.format(e)

if __name__ == "__main__":
    import time
    ND = ND1000S()
    while True:
        print(ND.grabdata() )
        print(ND.msg)
        time.sleep(5)

