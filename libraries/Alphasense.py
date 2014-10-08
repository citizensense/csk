#!/usr/bin/python3

class Alphasense:

    # Inititiaslise unique calibration values
    def __init__(self, calibration):
        # Electronic zero values
        self.c = calibration
        self.msg = ''
    
    # Calculate ppb values
    def readppb(self, sensor, we, ae, temp):
        n = self.tempcompensation(sensor, temp)
        if sensor == 'NO2': 
            wez = self.c['we1z']
            aez = self.c['ae1z']
            sensi = self.c['1sensi']
        if sensor == 'O3': 
            wez = self.c['we2z']
            aez = self.c['ae2z']
            sensi = self.c['2sensiO3']
        if sensor == 'O3no2': 
            wez = self.c['we2z']
            aez = self.c['ae2z']
            sensi = self.c['2sensiO3no2']
        if sensor == 'NO': 
            wez = self.c['we3z']
            aez = self.c['ae3z']
            sensi = self.c['3sensi']
        # Calculate our base millivolt values
        wemv = we-wez
        aemv = ae-(n*aez)
        if aemv < 0: aemv = 0
        mv = wemv-aemv
        ppb = mv/sensi
        self.msg = 'CALC {0}: \nwemv={1}-{2} = {3} \naemv={4}-({5}*{6}) = {8}\nmv={7}-{8} = {9} \nppb={9}/{10} ---------------------\n'.format(sensor, we, wez, wemv, ae, n, aez, wemv, aemv, mv, sensi)
        return ppb
 
    def readpidppm(self, pidout):
        self.msg = 'CALC PID:\n({}-45)/2'.format(pidout)
        return (pidout-45)/2

    # Compensated GAS mv
    def compGASmv(self, mvWE, mvAE):
        VPCBWE = self.weSN   # Value from calibration sheet
        VPCBAE = self.aeSN   # Value from calibration sheet
        VWE = mvWE          # Value read from electrode
        VAE = mvAE          # Value read from electrode
        N=self.tempcomp     # Temperature compensation value
        s1 = '('+str(VWE)+'-'+str(VPCBWE)+')'
        s2 = '-('+str(N)+'*('+str(VAE)+'-'+str(VPCBAE)+'))'
        # print('COMPmv: '+s1+s2)
        return (VWE-VPCBWE)-(N*(VAE-VPCBAE))
   
    # Calculate compensation variables
    def tempcompensation(self, sensor, temp):
        #print('READSENSOR=========:::'+sensor+' temp:'+str(temp))
        if sensor == 'NO2':
            if temp > -30: tempcomp = 1.09 # -30c to 19c = 1.09
            if temp > 20: tempcomp = 1.35  # 20c to 29c = 1.35
            if temp > 30: tempcomp = 2.0   # 30c to 50c = 2
        elif sensor == 'O3':
            if temp < 10: tempcomp = 0.75   # -30c to 9c = 0.75
            if temp > 10: tempcomp = 1.28  # 10c to 50c = 1.28
        elif sensor == 'O3no2':
            if temp < 20: tempcomp = 1.15  # -30c to 19c = 1.15
            if temp > 20: tempcomp = 1.82  # 20c to 29c = 1.82
            if temp > 30:  tempcomp = 3.93 # 30c to 50c = 3.93
        elif sensor == 'SO2':
            if temp < 20: tempcomp = 1.15  # -30c to 19c = 1.15
            if temp > 20: tempcomp = 1.82  # 20c to 29c = 1.82
            if temp > 30:  tempcomp = 3.93 # 30c to 50c = 3.93
        elif sensor == 'NO':
            if temp < 20: tempcomp = 1.48  # -30c to 19c = 1.48
            if temp > 20: tempcomp = 2.02  # 20c to 29c = 2.02
            if temp > 30: tempcomp = 1.72  # 30c to 50c = 1.72
        return tempcomp

if __name__ == "__main__":
    calibration = {
        'we1z':300,        # VpcbWE-SN1-zero 
        'we2z':409,        # VpcbWE-SN2-zero
        'we3z':281,        # VpcbWE-SN3-zero
        'ae1z':303,        # VpcbAE-SN1-zero
        'ae2z':419,        # VpcbAE-SN2-zero
        'ae3z':285,        # VpcbAE-SN3-zero
        '1sensi':0.423,   # "Sensitivity (mV/ppb)"
        '2sensiO3':0.290, # "Sensitivity (mV/ppb)"
        '2sensiO3no2':0.407,# "Sensitivity (mV/ppb)"
        '3sensi':0.367    # "Sensitivity (mV/ppb)" 
    }
    # Set the callibration numbers
    alphasense = Alphasense(calibration)
    # Ready to calculate values
    we = 500      # Millivolts
    ae = 400      # Millivolts
    pidout =  98.5678  # Millivilts
    temp = 20 # Degrees centigrade
    print('\nwe: {} ae: {} temp: {}'.format(we, ae, temp))
    print('NO2ppb: {} '.format(alphasense.readppb('NO2', we, ae, temp), ))
    print(alphasense.msg)
    print('O3ppb: {}'.format( alphasense.readppb('O3', we, ae, temp)) )
    print(alphasense.msg)
    print('O3NO2ppb: {}'.format( alphasense.readppb('O3no2', we, ae, temp)) )
    print(alphasense.msg)
    print('NOppb: {}\n'.format(alphasense.readppb('NO', we, ae, temp))  )
    print(alphasense.msg)
    print('PIDppm: {}\n'.format(alphasense.readpidppm(pidout))  )
    print(alphasense.msg)

