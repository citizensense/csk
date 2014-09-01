#!/bin/sh 

# Set the font & keyboartd
loadkeys uk
setfont ter-p24b.psf.gz

# Make USB bus power ediable: TODO: Doesn't need to be 777 just testing...
chmod 777 /sys/devices/platform/bcm2708_usb/bussuspend
chmod 777 /sys/devices/platform/bcm2708_usb/buspower

# Start an ultra minimal local server	
#killall python
#cd /home/csk/sensorcoms/public	 
#python -m http.server 80 &

# Run the sensor app 
#/home/csk/sensorcoms/app.py > /dev/null 2>&1
/home/csk/sensorcoms/app.py &

# Startup GPSD
killall gpsd
#gpsd -N -n -D 2 /dev/ttyUSB0 > /dev/null 2>&1
gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock &

# Check if we got to the end of the script
MYDATE=date
echo $MYDATE >> /home/csk/log.txt	 

