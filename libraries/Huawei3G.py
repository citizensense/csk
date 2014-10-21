#!/usr/bin/python3
import subprocess, logging, sys, time

# Class to grab data from a ND100S GPS unit
class Huawei3G:
    
    def __init__(self):
        self.rebootafter = 120 # Minutes until a reboot
        self.started = int(time.time())
        self.msg = ''
        self.strangecount = 0
    
    # TODO: Rework reboot
    def willrebootin(self):
        elapsed = int(time.time())-self.started
        secondstillreboot = (self.rebootafter*60)-elapsed
        return '{} seconds'.format(secondstillreboot)

    def checkconnection(self):
        # Because the dongles sometimes get stuck we need to reboot after a set amount of time
        # elapsed = int(time.time())-self.started
        # if elapsed >= self.rebootafter*60:
        #    subprocess.check_output("reboot", shell=True).decode("utf-8")
        # Setup base vars
        self.msg = "==========checkconnection()========"
        #self.msg += '\nWill reboot in: {}'.format(self.willrebootin())
        eth = -1
        wlan = -1
        wwan0 = -1
        # Search for a network interface
        try:
            ipa = subprocess.check_output("ip a", shell=True).decode("utf-8")
            eth1 = ipa.find('eth1')
            wlan0 = ipa.find('wlan0')
            wwan0 = ipa.find('wwan0')
        except Exception as e:
            self.msg += '\nError: couldn\'t run "ip a" | {} '.format(str(e))
            return False
        # If wwan0 is found the make sure the network is put up
        if wwan0 > -1:
            self.msg += "\nFound network device: wwan0"
            try:
                wwan0 = subprocess.check_output("ip a show wwan0", shell=True).decode("utf-8")
                if wwan0.find('UP') == -1:
                    self.msg += '\nNetwork device is DOWN: wwan0'
                    self.netctlstart('wwan0')
                    self.msg += '\nTry this script in a bit and see if we are connected'
                    return False
                else:
                    self.msg += '\nNetwork device is UP: wwan0'
                    if self.findip('wwan0').strip() == '192.168.1.99/24':
                        self.msg += "wwan0 Network looks good... "
                    return True
            except Exception as e: 
                self.msg += "Error: Unable to run ip a show eth1 | {} ".format(e)
                return False
        # If eth1 isnt found then reload the dongle
        if eth1 == -1:
            self.msg += "\nCouldn't find network device eth1"
            if self.findhuawei() is False:
                self.huawiereboot()
                return False
            else:
                self.msg += "\nHuawei: In correct mode" 
        # Or if it has been found, check we are connected to the network
        else:
            self.msg += "\nFound network device: eth1"
            try:
                eth1 = subprocess.check_output("ip a show eth1", shell=True).decode("utf-8")
                if eth1.find('UP') == -1:
                    self.msg += '\nNetwork device is DOWN: eth1'
                    self.netctlstart('eth1')
                    self.msg += '\nTry this script in a bit and see if we are connected'
                    return False
                else:
                    self.msg += '\nNetwork device is UP: eth1'
                    if self.findip('eth1').strip() == '192.168.1.99/24':
                        self.msg += "eth1 Network looks good... "
                    return True
            except Exception as e: 
                self.msg += "Error: Unable to run ip a show eth1 | {} ".format(e)
                return False
    
    # Switch the 3G dongle into network mode
    def huawiereboot(self):
        try:
            b = subprocess.check_output('usb_modeswitch -c /home/csk/csk/init/E353.config', shell=True).decode("utf-8")
            self.msg += "\nAttempted to switch 3G dongle to network mode: "
            return True
        except Exception as e:
            self.msg += "\nHuawei: usb_modeswitch not working | {}".format(e)
            return False
    
    # power on/off USB bus
    def usbpoweroffon(self):
        chmod = "chmod 777 /sys/devices/platform/bcm2708_usb/bussuspend"
        off = "echo '1' > /sys/devices/platform/bcm2708_usb/bussuspend"
        on = "echo '0' > /sys/devices/platform/bcm2708_usb/bussuspend"
        try:
            subprocess.check_output(chmod, shell=True).decode('utf-8')
            subprocess.check_output(off, shell=True).decode('utf-8')
            self.msg += "\nUSB bus power off"+str(b)
            time.sleep(0.2)
            subprocess.check_output(on, shell=True) 
            self.msg += "\nUSB bus power on"
        except Exception as e:
            self.msg += "\nError: USB bus power off/on: ".format(e)

    # Start the network configeration
    def netctlstart(self, device):
        try:
            # Restart the systemd service to allow auto connect of the network
            subprocess.check_output("netctl switch-to {}".format(device), shell=True).decode("utf-8")
            self.msg += '\nAttempted to start: {}'.format(device)
        except Exception as e:
            self.msg += "\nUnable to start: {}. May need to run script as root".format(device)           
    
    # Find the IP address of the attached entwoprk device
    def findip(self, device):
        try:
            cmd = "ip a show {0} | grep inet | cut -d' ' -f 6".format(device)
            IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
            self.msg += '\nIP address: {}'.format(IP)
            return IP
        except Exception as e:
            self.msg  += '\nError: Unable to find IP address | '.format(e)
            return False

    # See if we have a 3G dongle present
    def findhuawei(self):
        try:
            search = "Huawei Technologies Co., Ltd. E353/E3131"
            lsusb = subprocess.check_output("lsusb | grep Huawei", shell=True).decode("utf-8")
            self.msg += '\nHuawei mode: {}'.format(lsusb)
            if lsusb.find('Mass storage mode') != -1:
                self.msg += '\nHuawei: In mass storage mode'
                return False
            if lsusb.find(search) == -1: 
                self.msg += '\nHuawei: In a strange mode: Possibly no sim card!'
                self.strangecount += 1
                if self.strangecount >= 10:
                    subprocess.check_output("sudo reboot", shell=True).decode("utf-8")
                    self.strangecount = 0
                return False
            else: 
                return True
        except Exception as e:
            self.msg += '\nHuawei: Can\'t find dongle'
            return False

if __name__ == "__main__":
    import time
    network = Huawei3G()
    while True:
        resp = network.checkconnection() 
        print(resp)
        print(network.msg)
        time.sleep(5)

# OLDER DONGLES
 # Example output with 3G dongle in network device mode
 # Bus 001 Device 024: ID 12d1:14db Huawei Technologies Co., Ltd. E353/E3131
 
 # In MAss Storage mode
 # Bus 001 Device 006: ID 12d1:1f01 Huawei Technologies Co., Ltd. E353/E3131 (Mass storage mode)

# NEWER DONGLES
  # Bus 001 Device 007: ID 12d1:1c1e Huawei Technologies Co., Ltd. 

  # Bus 001 Device 006: ID 12d1:14fe Huawei Technologies Co., Ltd. Modem (Mass Storage Mode)
