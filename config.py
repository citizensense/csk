#!/usr/bin/python3
import json, subprocess, time

# Construct the config for this sspecific device
def init():

    # Config values
    CONFIG = {
        'dbfile':'data/db.sqlite3',
        #'posturl':'http://192.168.1.100:8787/api',
        'posturl':'http://frackbox.citizensense.net/api',
        '0000000080c169f1':{
            'name':'kit 1',
            'alphasense':{
                'weSN1':0,        # VpcbWE-SN1-zero 
                'weSN2':0,        # VpcbWE-SN2-zero
                'weSN3':0,        # VpcbWE-SN3-zero
                'aeSN1':0,        # VpcbAE-SN1-zero
                'aeSN2':0,        # VpcbAE-SN2-zero
                'aeSN3':0,        # VpcbAE-SN3-zero
                'SN1sensi':0.0,   # "Sensitivity (mV/ppb)"
                'SN2sensi':0.0,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.0    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '000000006217b4aa':{
            'name':'kit 2',
            'alphasense':{
                'weSN1':300,        # VpcbWE-SN1-zero 
                'weSN2':409,        # VpcbWE-SN2-zero
                'weSN3':281,        # VpcbWE-SN3-zero
                'aeSN1':303,        # VpcbAE-SN1-zero
                'aeSN2':419,        # VpcbAE-SN2-zero
                'aeSN3':285,        # VpcbAE-SN3-zero
                'SN1sensi':0.423,   # "Sensitivity (mV/ppb)"
                'SN2sensiO3':0.290, # "Sensitivity (mV/ppb)"
                'SN2sensiNO2':0.407,# "Sensitivity (mV/ppb)"
                'SN3sensi':0.367    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '0000000008e366f4':{
            'name':'kit 3',
            'alphasense':{
                'weSN1':320,        # VpcbWE-SN1-zero 
                'weSN2':419,        # VpcbWE-SN2-zero
                'weSN3':269,        # VpcbWE-SN3-zero
                'aeSN1':317,        # VpcbAE-SN1-zero
                'aeSN2':415,        # VpcbAE-SN2-zero
                'aeSN3':267,        # VpcbAE-SN3-zero
                'SN1sensi':0.479,   # "Sensitivity (mV/ppb)"
                'SN2sensi03':0.293, # "Sensitivity (mV/ppb)"
                'SN2sensiNO2':0.382,
                'SN3sensi':0.371    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '00000000b6e2f676':{
            'name':'kit 4',
            'alphasense':{
                'weSN1':299,        # VpcbWE-SN1-zero 
                'weSN2':409,        # VpcbWE-SN2-zero
                'weSN3':267,        # VpcbWE-SN3-zero
                'aeSN1':309,        # VpcbAE-SN1-zero
                'aeSN2':419,        # VpcbAE-SN2-zero
                'aeSN3':284,        # VpcbAE-SN3-zero
                'SN1sensi':0.376,   # "Sensitivity (mV/ppb)"
                'SN2sensiO3':0.404, # "Sensitivity (mV/ppb)"
                'SN2sensiNO2':0.416
                'SN3sensi':0.352    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '00000000cb78dc37':{
            'name':'kit 5',
            'alphasense':{
                'weSN1':305,        # VpcbWE-SN1-zero 
                'weSN2':351,        # VpcbWE-SN2-zero
                'weSN3':266,        # VpcbWE-SN3-zero
                'aeSN1':313,        # VpcbAE-SN1-zero
                'aeSN2':435,        # VpcbAE-SN2-zero
                'aeSN3':284,        # VpcbAE-SN3-zero
                'SN1sensi':0.314,   # "Sensitivity (mV/ppb)"
                'SN2sensiO3':0.351, # "Sensitivity (mV/ppb)"
                'SN2sensiNO2':0.420,
                'SN3sensi':0.380    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '000000003068b18f':{
            'name':'kit 6',
            'alphasense':{
                'weSN1':0,        # VpcbWE-SN1-zero 
                'weSN2':0,        # VpcbWE-SN2-zero
                'weSN3':0,        # VpcbWE-SN3-zero
                'aeSN1':0,        # VpcbAE-SN1-zero
                'aeSN2':0,        # VpcbAE-SN2-zero
                'aeSN3':0,        # VpcbAE-SN3-zero
                'SN1sensi':0.,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.,    # "Sensitivity (mV/ppb)"
                'SN3sensi':0.     # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        }
    }
    
    # Load the config for this specific device
    loaded = False
    while loaded is not True:
        try:
            jsonstr = subprocess.check_output("/home/csk/csk/libraries/RPiInfo.sh", shell=True).decode("utf-8")
            info=json.loads(jsonstr)
            serial = info["serial"] 
            MAC = info["MAC"]
            CONFIG[serial]['MAC'] = MAC 
            CONFIG[serial]['serial'] = serial
            CONFIG[serial]['posturl'] = CONFIG['posturl']
            CONFIG[serial]['dbfile'] = CONFIG['dbfile'] 
            loaded = True
        except Exception as e:
            print(e)
        time.sleep(10)
    return CONFIG[serial]

if __name__=='__main__':
    print(init())

