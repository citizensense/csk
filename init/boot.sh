#!/bin/sh 
# Script is called via systemd on boot

# Set the font & keyboard: TODO: Make perminent 
loadkeys uk
setfont ter-p24b.psf.gz

# Run the sensor app 
cd /home/csk/csk
./app.py > /dev/null &

# Check if we got to the end of the script
MYDATE=$(date)
echo "$MYDATE: Started GPSD and app.py application" >> /home/csk/csk/csk.log 

