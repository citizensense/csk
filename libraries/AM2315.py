#!/usr/bin/env python3
import quick2wire.i2c as i2c 
import array, sys, time, math

class AM2315(object):

    def __init__(self):
        self.R_CONST=8314.3
        self.MW_CONST=18.016
        self.AM2315_I2CADDR = 0x5c
        self.AM2315_WAITTIME = 0.150
        self.MAXTRYS=3
        self.FUNCTION_CODE_READ = 0x03
        self.readBytes = array.array ("B",[0x00,0x04])
        pass

    def __del__(self):
        pass
    
    def values(self):
        i=0
        errcode=0
        hum = 999 
        temp = 999 
        while i <= self.MAXTRYS:
          with i2c.I2CMaster() as bus:
            try:
               bus.transaction(i2c.writing_bytes(self.AM2315_I2CADDR,
                   self.FUNCTION_CODE_READ,*self.readBytes ))
               time.sleep(self.AM2315_WAITTIME)
               read_results = bus.transaction(i2c.reading(self.AM2315_I2CADDR, 8)) 
#               print(read_results)
               break
            except:
               i = i+1 
        if i > self.MAXTRYS:
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

    def SDD(self,T,mode):
        return 6.1078 * math.pow(10,((self.a(mode)*T)/(self.b(mode)+T)))
    
    def DD(self,mode):
        r = self.humidity()
        T = self.temperature()
        return r/100 * self.SDD(T,mode)
    
    def a(self,mode):
        T = self.temperature()
        if T >= 0:
           return 7.5
        if T < 0 and mode == 0 :
           return 7.6
        if T < 0 and mode == 1 :
           return 9.5
    
    def b(self,mode):
        T = self.temperature()
        if T >= 0:
           return 237
        if T < 0 and mode == 0 :
           return 240.7
        if T < 0 and mode == 1 :
           return 265.5
    
    def TD(self,mode):
        v=math.log10(self.DD(mode)/6.1078)
        return (self.b(mode)*v)/(self.a(mode)-v)
    
    def RR(self,mode):
        T = self.temperature()
        return 100*self.SDD(self.TD(T),mode) / self.SDD(T,mode)
    
    def AFr(self,mode):
        T = self.temperature()
        return math.pow(10,5)*self.MW_CONST/self.R_CONST*self.DD(mode)/self.TK(T)
    
    def TK(self,T):
        return T+273.15
    
    def crc16(self, char):
         crc = 0xFFFF
         for l in char:
               crc = crc ^ l
               for i in range(1,9):
                   if (crc & 0x01):
                      crc = crc >> 1
                      crc = crc ^ 0xA001
                   else:
                      crc = crc >> 1
         return crc

# Example
if __name__ ==  "__main__":
    sensor=AM2315()
    temp = sensor.temperature() 
    humid = sensor.humidity()
    print('TEMP: '+str(temp))
    print('HUMID: '+str(humid))
