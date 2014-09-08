import serial
speck = serial.Serial('/dev/ttyAMA0', 9600)
print('Opened Speck Serial Comms')
while 1:
    line=speck.readline()
    print(line)
speck.close()
