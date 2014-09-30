#!/usr//bin/python2
import spidev, time, json

spi = spidev.SpiDev()
spi.open(0,0)

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    r = spi.xfer2([1,(8+adcnum)<<4,0])
    adcout = ((r[1]&3) << 8) + r[2]
    return adcout

# Read all the channels and output as JSON
def readall():
    vals = []
    for channel in range(0,8):
        string = '"{}":{}'.format(channel, readadc(channel))
        vals.append(string)
    print(vals)
    return  '{{}}'.format(','.join(vals))

while True:
    print( readall() )
    time.sleep(1)
