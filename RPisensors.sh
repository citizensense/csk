HEAD="<pre>"
s="</pre><hr /><pre>"
TEMP=$(/opt/vc/bin/vcgencmd measure_temp)
VOLTS=$(/opt/vc/bin/vcgencmd measure_volts)
GPU=$(/opt/vc/bin/vcgencmd get_mem arm/gpu)
MEM=$(free -mh | grep '+ buffers')
LOAD=$(uptime)
TIME=$(date +%S)
INFO=$(cat /proc/cpuinfo)
FOOT="</pre>"
echo -e "$HEAD RaspberryPi $TEMP $s $GPU $s $MEM $s $LOAD $s $TIME $s $INFO $s $FOOT" > /home/csk/index.html
