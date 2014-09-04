#!/bin/sh 
# Script is called from systemd on boot

# Set the font & keyboard: TODO: Possible make perminent 
loadkeys uk
setfont ter-p24b.psf.gz

# Run the sensor app 
#/home/csk/sensorcoms/app.py > /dev/null 2>&1
/home/csk/csk/app.py &

# Startup GPSD
killall gpsd
#gpsd -N -n -D 2 /dev/ttyUSB0 > /dev/null 2>&1
gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock &

# Check if we got to the end of the script
MYDATE=date
echo "$MYDATE: Started GPSD and app.py application" >> /home/csk/csk.log 

