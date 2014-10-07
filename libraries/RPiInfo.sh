TEMP=$(/opt/vc/bin/vcgencmd measure_temp | cut -d= -f2)
DISKAVAILABLE=$(df -h | grep '/dev/root' | cut -d' ' -f12)
DISKUSED=$(df -h | grep '/dev/root' | cut -d' ' -f14)
VOLTS=$(/opt/vc/bin/vcgencmd measure_volts)
#GPU=$(/opt/vc/bin/vcgencmd get_mem arm/gpu)
MEM=$(free -mh | grep '+ buffers')
L1=$(uptime | cut -d' ' -f12 | rev | cut -c 2- | rev)
L2=$(uptime | cut -d' ' -f13 | rev | cut -c 2- | rev)
L3=$(uptime | cut -d' ' -f14 | rev | cut -c 2- | rev)
MAC=$(ip link show eth1 | grep link/ether | cut -d' ' -f6)
if [ -z "$MAC" ]; then
    MAC=$(ip link show wlan0 | grep link/ether | cut -d' ' -f6)
fi
if [ -z "$MAC" ]; then
    MAC=$(ip link show wwan0 | grep link/ether | cut -d' ' -f6)
fi
if [ -z "$MAC" ]; then
    MAC="no-network-interface"
fi
#LOAD=$(awk "BEGIN{printf(\"%2.2f\n\", ($L1+$L2+$L3)/3); exit }")
INFO=$(cat /proc/cpuinfo)
SERIAL=$(cat /proc/cpuinfo | grep Serial | cut -f3 | cut -c 3-)
echo -e "{\"tempc\":\"$TEMP\",\"disk%used\":\"$DISKUSED\",\"diskavailable\":\"$DISKAVAILABLE\",\"load\":\"$L1-$L2-$L3\",\"serial\":\"$SERIAL\",\"MAC\":\"$MAC\"}" 
