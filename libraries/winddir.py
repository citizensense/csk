#!/usr/bin/python3
# Maplins wind direction sensor
import json

# Small class to convert a resistance value to a compass point
class winddir:

    def __init__(self):
        # Amount to brack ether side of the 'sweet spot'
        self.bracket = 10

    def compass(self, res):
        if self.isrange(781, res): return 'N'
        if self.isrange(463, res): return 'NE'
        if self.isrange(93, res): return 'E'
        if self.isrange(185, res): return 'SE'
        if self.isrange(288, res): return 'S'
        if self.isrange(630, res): return 'SW'
        if self.isrange(932, res): return 'W'
        if self.isrange(878, res): return 'NW'

    def isrange(self, isit, val):
        mmax = isit+self.bracket
        mmin = isit-self.bracket
        if val <= mmax and val >= mmin: return True
        else: return False

if __name__=='__main__':
    import subprocess, time
    wind = winddir()
    # Read the wind direction
    while True:
        # First grab a value from the adc
        try:
            jsonstr = subprocess.check_output("./MCP3008.py", shell=True).decode("utf-8")
            adc=json.loads(jsonstr)
            val = adc['5']
        except Exception as e:
            print('No ADC: '+str(e))
            val = False
        # Now convert it to a compass reading
        if val:
            point = wind.compass(val)
            print(str(val)+': '+point)
        time.sleep(1)
