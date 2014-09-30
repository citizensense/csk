#!/usr//bin/python2
import spidev, json

class mcp3008():
    
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(0,0)

    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(self, adcnum):
        if ((adcnum > 7) or (adcnum < 0)):
            return -1
        r = self.spi.xfer2([1,(8+adcnum)<<4,0])
        adcout = ((r[1]&3) << 8) + r[2]
        return adcout

    # Read all the channels and output as JSON
    def readall(self):
        vals = {}
        for channel in range(0,8):
            vals[channel] = self.readadc(channel)
        return  json.dumps(vals)

if __name__=='__main__':
    adc = mcp3008()
    print( adc.readall() )

