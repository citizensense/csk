#! /bin/sh
sleep 1
echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
sleep 5
hwclock -s
