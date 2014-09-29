#!/usr/bin/env python3
#
import quick2wire.i2c as i2c 
import array
import sys 
import time
import math
#
R_CONST=8314.3
MW_CONST=18.016
AM2315_I2CADDR = 0x5c
AM2315_WAITTIME = 0.150
MAXTRYS=3
FUNCTION_CODE_READ = 0x03
readBytes = array.array ("B",[0x00,0x04])
class AM2315(object):
    def __init__(self):
        pass
    def __del__(self):
        pass
    def values(self):
        i=0
        errcode=0
        hum = 999 
        temp = 999 
        while i <= MAXTRYS:
          with i2c.I2CMaster() as bus:
            try:
               bus.transaction(i2c.writing_bytes(AM2315_I2CADDR,
                   FUNCTION_CODE_READ,*readBytes ))
               time.sleep(AM2315_WAITTIME)
               read_results = bus.transaction(i2c.reading(AM2315_I2CADDR, 8)) 
#               print(read_results)
               break
            except:
               i = i+1 
        if i > MAXTRYS:
           errcode=1
        else:
           s=bytearray(read_results[0])
           crc = 256*s[7]+s[6]
           t = bytearray([s[0],s[1],s[2],s[3],s[4],s[5]])
           c = self.crc16(t)
           if crc != c:
             errcode=2
           else:
             hum = (256*s[2]+s[3])/10
             temp = (256*s[4]+s[5])/10
        return hum,temp,errcode   
    def humidity(self):
        x=self.values()
        return self.values()[0]

    def temperature(self):
        return self.values()[1]
