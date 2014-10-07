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
                'we1z':0,         # VpcbWE-SN1-zero 
                'we2z':0,         # VpcbWE-SN2-zero
                'we3z':0,         # VpcbWE-SN3-zero
                'ae1z':0,         # VpcbAE-SN1-zero
                'ae2z':0,         # VpcbAE-SN2-zero
                'ae3z':0,         # VpcbAE-SN3-zero
                '1sensi':0.0,     # "Sensitivity (mV/ppb)"
                '2sensi':0.0,     # "Sensitivity (mV/ppb)"
                '3sensi':0.0      # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '000000006217b4aa':{
            'name':'kit 2',
            'alphasense':{
                'we1z':300,        # VpcbWE-SN1-zero 
                'we2z':409,        # VpcbWE-SN2-zero
                'we3z':281,        # VpcbWE-SN3-zero
                'ae1z':303,        # VpcbAE-SN1-zero
                'ae2z':419,        # VpcbAE-SN2-zero
                'ae3z':285,        # VpcbAE-SN3-zero
                '1sensi':0.423,    # "Sensitivity (mV/ppb)"
                '2sensiO3':0.290,  # "Sensitivity (mV/ppb)"
                '2sensiO3no2':0.407, # "Sensitivity (mV/ppb)"
                '3sensi':0.367     # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '0000000008e366f4':{
            'name':'kit 3',
            'alphasense':{
                'we1z':320,        # VpcbWE-SN1-zero 
                'we2z':419,        # VpcbWE-SN2-zero
                'we3z':269,        # VpcbWE-SN3-zero
                'ae1z':317,        # VpcbAE-SN1-zero
                'ae2z':415,        # VpcbAE-SN2-zero
                'ae3z':267,        # VpcbAE-SN3-zero
                '1sensi':0.479,    # "Sensitivity (mV/ppb)"
                '2sensiO3':0.293,  # "Sensitivity (mV/ppb)"
                '2sensiO3no2':0.382,
                '3sensi':0.371     # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '00000000b6e2f676':{
            'name':'kit 4',
            'alphasense':{
                'we1z':299,        # VpcbWE-SN1-zero 
                'we2z':409,        # VpcbWE-SN2-zero
                'we3z':267,        # VpcbWE-SN3-zero
                'ae1z':309,        # VpcbAE-SN1-zero
                'ae2z':419,        # VpcbAE-SN2-zero
                'ae3z':284,        # VpcbAE-SN3-zero
                '1sensi':0.376,    # "Sensitivity (mV/ppb)"
                '2sensiO3':0.404,  # "Sensitivity (mV/ppb)"
                '2sensiO3no2':0.416,
                '3sensi':0.352     # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '00000000cb78dc37':{
            'name':'kit 5',
            'alphasense':{
                'we1z':305,        # VpcbWE-SN1-zero 
                'we2z':351,        # VpcbWE-SN2-zero
                'we3z':266,        # VpcbWE-SN3-zero
                'ae1z':313,        # VpcbAE-SN1-zero
                'ae2z':435,        # VpcbAE-SN2-zero
                'ae3z':284,        # VpcbAE-SN3-zero
                '1sensi':0.314,    # "Sensitivity (mV/ppb)"
                '2sensiO3':0.351,  # "Sensitivity (mV/ppb)"
                '2sensiO3no2':0.420,
                '3sensi':0.380     # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '000000003068b18f':{
            'name':'kit 6',
            'alphasense':{
                'we1z':0,        # VpcbWE-SN1-zero 
                'we2z':0,        # VpcbWE-SN2-zero
                'we3z':0,        # VpcbWE-SN3-zero
                'ae1z':0,        # VpcbAE-SN1-zero
                'ae2z':0,        # VpcbAE-SN2-zero
                'ae3z':0,        # VpcbAE-SN3-zero
                '1sensi':0.0,    # "Sensitivity (mV/ppb)"
                '2sensiO3':0.0,  # "Sensitivity (mV/ppb)"
                '2sensiO3no2':0.0,
                '3sensi':0.0     # "Sensitivity (mV/ppb)" 
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

