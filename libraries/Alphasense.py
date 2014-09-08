#!/usr/bin/python3

class Alphasense:

    # Inititiaslise unique calibration values
    def __init__(self, weSN1, weSN2, weSN3, aeSN1, aeSN2, aeSN3, SN1sensi, SN2sensi, SN3sensi):
        # Electronic zero values provided on callibration certificate
        self.weSN1 = weSN1     # VpcbWE-SN1-zero 
        self.weSN2 = weSN2     # VpcbWE-SN2-zero
        self.weSN3 = weSN3     # VpcbWE-SN3-zero
        self.aeSN1 = aeSN1     # VpcbAE-SN1-zero
        self.aeSN2 = aeSN2     # VpcbAE-SN2-zero
        self.aeSN3 = aeSN3     # VpcbAE-SN3-zero
        self.SN1sensi = SN1sensi    # "Sensitivity (mV/ppb)"
        self.SN2sensi = SN1sensi    # "Sensitivity (mV/ppb)"
        self.SN3sensi = SN3sensi    # "Sensitivity (mV/ppb)"

    # Compensated GAS mv
    def compGASmv(self, mvWE, mvAE):
        VPCBWE = self.weSN   # Value from calibration sheet
        VPCBAE = self.aeSN   # Value from calibration sheet
        VWE = mvWE          # Value read from electrode
        VAE = mvAE          # Value read from electrode
        N=self.tempcomp     # Temperature compensation value
        return (VWE-VPCBWE)-(N*(VAE-VPCBAE))

    # Calculate ppb values
    def readppb(self, sensor, mvWE, mvAE, temp):
        # Calulate compensation values
        self.setcompensation(sensor, temp)
        # Millivolt compensation value for the sensor being read
        compmv = self.compGASmv(mvWE, mvAE) 
        # Return parts per billion
        return compmv/self.sensitivity
    
    # Setup compensation variables
    def setcompensation(self, sensor, temp):
        if sensor == 'NO2a4':
            weSN = self.weSN1
            aeSN = self.aeSN1
            sensi = self.SN1sensi
            if temp >= -30: tempcomp = 1.09 # -30c to 19c = 1.09
            if temp >= 20: tempcomp = 1.35  # 20c to 29c = 1.35
            if temp >= 30: tempcomp = 2.0   # 30c to 50c = 2
        elif sensor == 'O3a4':
            weSN = self.weSN2
            aeSN = self.aeSN2
            sensi = self.SN2sensi
            if temp <= 9: tempcomp = 0.75   # -30c to 9c = 0.75
            if temp >= 10: tempcomp = 1.28  # 10c to 50c = 1.28
        elif sensor == 'SO2a4':
            weSN = self.weSN3
            aeSN = self.aeSN3
            sensi = self.SN3sensi
            if temp <= 19: tempcomp = 1.15  # -30c to 19c = 1.15
            if temp >= 20: tempcomp = 1.82  # 20c to 29c = 1.82
            if temp >= 30:  tempcomp = 3.93 # 30c to 50c = 3.93
        elif sensor == 'NOa4':
            weSN = self.weSN3
            aeSN = self.aeSN3
            sensi = self.SN3sensi
            if temp <= 19: tempcomp = 1.48  # -30c to 19c = 1.48
            if temp >= 20: tempcomp = 2.02  # 20c to 29c = 2.02
            if temp >= 30: tempcomp = 1.72  # 30c to 50c = 1.72
        self.tempcomp = tempcomp
        self.weSN = weSN
        self.aeSN = aeSN
        self.sensitivity = sensi

if __name__ == "__main__":
    # Electronic zero values provided on callibration certificate
    weSN1 = 310     # VpcbWE-SN1-zero 
    weSN2 = 412     # VpcbWE-SN2-zero
    weSN3 = 280     # VpcbWE-SN3-zero
    aeSN1 = 312     # VpcbAE-SN1-zero
    aeSN2 = 413     # VpcbAE-SN2-zero
    aeSN3 = 270     # VpcbAE-SN3-zero
    SN1sensi = 0.54     # "Sensitivity (mV/ppb)"
    SN2sensi = 0.238    # "Sensitivity (mV/ppb)"
    SN3sensi = 0.362    # "Sensitivity (mV/ppb)"
    alphasense = Alphasense(weSN1, weSN2, weSN3, aeSN1, aeSN2, aeSN3, SN1sensi, SN2sensi, SN3sensi)
    # Ready to calculate values
    mvWE = 862 # Millivolts
    mvAE = 312 # Millivolts
    temp = 23  # Degrees centigrade
    print('NO2ppb: '+str( alphasense.readppb('NO2a4', mvWE, mvAE, temp)) )
    print('O3ppb: '+str( alphasense.readppb('O3a4', mvWE, mvAE, temp)) )
    print('SO2ppb: '+str(alphasense.readppb('SO2a4', mvWE, mvAE, temp))  )



