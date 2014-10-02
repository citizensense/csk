#!/usr/bin/python3
import json, subprocess, time

# Construct the config for this sspecific device
def init():

    # Config values
    CONFIG = {
        'dbfile':'data/db.sqlite3',
        'posturl':'http://frackbox.citizensense.net/api',
        '0000000080c169f1':{
            'name':'kit 1',
            'alphasense':{
                'weSN1':310,        # VpcbWE-SN1-zero 
                'weSN2':412,        # VpcbWE-SN2-zero
                'weSN3':280,        # VpcbWE-SN3-zero
                'aeSN1':312,        # VpcbAE-SN1-zero
                'aeSN2':413,        # VpcbAE-SN2-zero
                'aeSN3':270,        # VpcbAE-SN3-zero
                'SN1sensi':0.54,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.238,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.362    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '0':{
            'name':'kit 2',
            'alphasense':{
                'weSN1':310,        # VpcbWE-SN1-zero 
                'weSN2':412,        # VpcbWE-SN2-zero
                'weSN3':280,        # VpcbWE-SN3-zero
                'aeSN1':312,        # VpcbAE-SN1-zero
                'aeSN2':413,        # VpcbAE-SN2-zero
                'aeSN3':270,        # VpcbAE-SN3-zero
                'SN1sensi':0.54,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.238,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.362    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '0000000008e366f4':{
            'name':'kit 3',
            'alphasense':{
                'weSN1':310,        # VpcbWE-SN1-zero 
                'weSN2':412,        # VpcbWE-SN2-zero
                'weSN3':280,        # VpcbWE-SN3-zero
                'aeSN1':312,        # VpcbAE-SN1-zero
                'aeSN2':413,        # VpcbAE-SN2-zero
                'aeSN3':270,        # VpcbAE-SN3-zero
                'SN1sensi':0.54,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.238,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.362    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '00000000b6e2f676':{
            'name':'kit 4',
            'alphasense':{
                'weSN1':310,        # VpcbWE-SN1-zero 
                'weSN2':412,        # VpcbWE-SN2-zero
                'weSN3':280,        # VpcbWE-SN3-zero
                'aeSN1':312,        # VpcbAE-SN1-zero
                'aeSN2':413,        # VpcbAE-SN2-zero
                'aeSN3':270,        # VpcbAE-SN3-zero
                'SN1sensi':0.54,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.238,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.362    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '00000000cb78dc37':{
            'name':'kit 5',
            'alphasense':{
                'weSN1':310,        # VpcbWE-SN1-zero 
                'weSN2':412,        # VpcbWE-SN2-zero
                'weSN3':280,        # VpcbWE-SN3-zero
                'aeSN1':312,        # VpcbAE-SN1-zero
                'aeSN2':413,        # VpcbAE-SN2-zero
                'aeSN3':270,        # VpcbAE-SN3-zero
                'SN1sensi':0.54,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.238,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.362    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        },
        '0':{
            'name':'kit 6',
            'alphasense':{
                'weSN1':310,        # VpcbWE-SN1-zero 
                'weSN2':412,        # VpcbWE-SN2-zero
                'weSN3':280,        # VpcbWE-SN3-zero
                'aeSN1':312,        # VpcbAE-SN1-zero
                'aeSN2':413,        # VpcbAE-SN2-zero
                'aeSN3':270,        # VpcbAE-SN3-zero
                'SN1sensi':0.54,    # "Sensitivity (mV/ppb)"
                'SN2sensi':0.238,   # "Sensitivity (mV/ppb)"
                'SN3sensi':0.362    # "Sensitivity (mV/ppb)" 
            },
            'methane':False
        }
    }
    
    # Load the config for this specific device
    loaded = False
    while loaded is not True:
        try:
            jsonstr = subprocess.check_output("libraries/RPiInfo.sh", shell=True).decode("utf-8")
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

