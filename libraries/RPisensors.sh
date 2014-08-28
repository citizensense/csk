HEAD="<pre>"
s="</pre><hr /><pre>"
DATE=$(date)
TEMP=$(/opt/vc/bin/vcgencmd measure_temp)
VOLTS=$(/opt/vc/bin/vcgencmd measure_volts)
GPU=$(/opt/vc/bin/vcgencmd get_mem arm/gpu)
MEM=$(free -mh | grep '+ buffers')
LOAD=$(uptime)
INFO=$(cat /proc/cpuinfo)
FOOT="</pre>"
echo -e "$HEAD RaspberryPi: $DATE $TEMP $s $GPU $s $MEM $s $LOAD $s $INFO $s $FOOT" > /home/csk/sensorcoms/public/index.html
