#!/usr/bin/python3
#############################################################################
# Application used to Asynchronously:                               #
#   1. Grab sensor data 
#   2. Save to local csv file                                               #
#   3. Send to server                                                       #
#############################################################################
# Include the 'libraries folder' in the system path
import sys, os, time, logging, threading, subprocess, urllib
from collections import OrderedDict
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(path, 'libraries') ) 
#import wiringpi2
import config
from datetime import datetime
from Huawei3G import *
from ND1000S import *
from SaveData import *
from CherryPyWebServer import *
from Alphasense import *
from AM2315 import *
from PostData import *
from database import *
from winddir import winddir

# The application class
class GrabSensors:
    
    # Initialise the object
    def __init__(self):
        # vars to keep track of the health of the system
        self.counter = 0
        self.timepassed = 0
        self.healthcheck = {}
        self.failedposts = 0
        # Load the config for this device
        self.log('INFO', 'Attempt to load the config')
        self.CONFIG = config.init()
        # Setup logging
        logging.basicConfig(filename='/home/csk/csk/csk.log', level=logging.DEBUG)
        self.log('INFO', 'Started script')
        # Setup means to save and post data to the server
        dbstruct = self.dbstructure()
        db = Database(self.CONFIG['dbfile'], dbstruct)
        self.log('INFO', db.printmsg() )  
        # Build a new database if need be
        db.build()
        self.log('INFO', db.printmsg())  
        # A class to help us post data
        self.poster = PostData()
        # Setup some base variables
        self.lock = threading.Lock()
        self.datapath = os.path.join(os.path.dirname(__file__), 'data/data.csv')
        self.H3G = Huawei3G()
        self.save = SaveData()
        self.temp = 999      # These get set by an external temperature sensor
        self.humid = 999     # These get set by an external humidity sensor
        # Start the webserver (runs in its own thread)
        globalconfig = {'server.socket_host':"0.0.0.0", 'server.socket_port':80 } 
        localconfig = {'/': {'tools.staticdir.root': '/home/csk/csk/public'}}
        self.webserver = CherryPyWebServer(globalconfig, localconfig) 
        self.webserver.setcontent('Started the server', ' ')
        # Data model: (shortname, [logtitle, values, max, min])
        self.datamodel = OrderedDict([
            ('lat',             ['USB-ND1000S',     []  ]),
            ('lon',             ['ND1000S-LON',     []  ]),
            ('speed',           ['ND1000S-SPEED',   []  ]),
            ('alt',             ['ND1000S-ALT',     []  ]),
            ("XTemp",         ['',    []  ]),
            ("XHumid",        ['',    []  ]),
            ('winddir',         ['SPI-8ADC--MCP3008-WindDirection',         []  ]),
            ('NOppb',          ['',    []  ]),
            ('O3ppb',           ['',    []  ]),
            ('O3no2ppb',           ['',    []  ]),
            ('NO2ppb',          ['',    []  ]),
            ('PIDppm',           ['',    []  ]),
            ('PID',             ['A1->16ADC->I2C',  []  ]),
            ('NOwe3',          ['A2->16ADC->I2C',  []  ]),
            ('NOae3',          ['A3->16ADC->I2C',  []  ]),
            ('O3we2',           ['A4->16ADC->I2C',  []  ]),
            ('O3ae2',           ['A5->16ADC->I2C',  []  ]),
            ('NO2we1',          ['A6->16ADC->I2C',  []  ]),
            ('NO2ae1',          ['A7->16ADC->I2C',  []  ]),
            ('PT+',             ['A8->16ADC->I2C',  []  ]),
            ('CPU',             ['RPi-TempC',       []  ]),
            ('Disk',            ['RPi-diskAvail',   []  ]),
            ('Load',            ['Rpi-CPU Load Ave',[]  ]),
            ('network',         ['HuaweiAvailable', []  ])
        ])
        # Place to store asychronosly generated values
        self.csvbuffer = OrderedDict([])
        # Initialise a list of threads so data can be aquired asynchronosly
        threads = []
        threads.append(threading.Thread(target=self.timepassing) )      # Keep track of how much time has passed
        threads.append(threading.Thread(target=self.checknetwork) )     # Check and sort out network
        threads.append(threading.Thread(target=self.grabgps) )          # Grab GPS data
        threads.append(threading.Thread(target=self.grabrpiinfo) )      # Grab RaspberryPi Info
        threads.append(threading.Thread(target=self.savedata) )         # Save Data to webGUI ans LogFile
        threads.append(threading.Thread(target=self.grabtemphumid) )    # Grab External temperature and humidity
        threads.append(threading.Thread(target=self.grabalphasense) )   # Grab data from alphasense via an ABEelectronics ADC 
        threads.append(threading.Thread(target=self.grabwinddir) )      # Grab data from wind direction sensor
        threads.append(threading.Thread(target=self.postdata) )         # Post data to server
        threads.append(threading.Thread(target=self.setweb) )           # Set data on the web interface
        for item in threads:
            item.start()
        self.healthcheck['---init()---'] = self.counter
        self.healthcheck['timepassing'] = self.counter
        self.healthcheck['checknetwork'] = self.counter
        self.healthcheck['grabgps'] = self.counter
        self.healthcheck['grabrpiinfo'] = self.counter
        self.healthcheck['savedata'] = self.counter
        self.healthcheck['grabtemphumid'] = self.counter
        self.healthcheck['grabalphasense'] = self.counter
        self.healthcheck['grabwinddir'] = self.counter
        self.healthcheck['postdata'] = self.counter
        self.healthcheck['setweb'] = self.counter
        # Setup GPOI Pin access
        #wiringpi2.wiringPiSetup() # For sequencial pin numbering i.e [] in pin layout below
        #wiringpi2.wiringPiSetupGpio() # For GPIO pin numbering
    
    # The database model to save data in
    def dbstructure(self):
        # The database model
        dbstruct = OrderedDict([
            # A place to store csvs
            ('csvs', [
                ('cid', 'INTEGER PRIMARY KEY'),
                ('timestamp', 'INTEGER'),
                ('csv', 'TEXT'),
                ('uploaded', 'INTEGER') # 0=notuploaded 1=uploaded
            ])
        ])
        return dbstruct
    
    # Counter to keep track of how much time has passed
    def timepassing(self):
        while True:
            self.counter = self.counter+1
            # Reboot once a day just in case...
            if self.counter > (60*60)*24:
                subprocess.check_output("reboot", shell=True).decode("utf-8")
            time.sleep(1)
            self.healthcheck['timepassing'] = self.counter

    # If any threads have new data then save it here
    def newdata(self, key, value, timecode = False):
        # TODO: Need to check the Rpi has the right time, otherwise we shouldn't save
        if timecode == False:
            timecode = int(time.time())
        # Create a lock so multiple threads don't get confused
        self.lock.acquire()
        try:
            keyindex = list(self.datamodel.keys()).index(key)
            # Create a buffer with n list locations to store this data if needed
            if timecode not in self.csvbuffer: 
                self.csvbuffer[timecode] = [""]*len(self.datamodel)
            # Save to our csv buffer, ready for saving to the log
            self.csvbuffer[timecode][keyindex] = ""+str(value)
            # save the last n values to our model
            if len(self.datamodel[key][1]) > 4:
                self.datamodel[key][1].pop(0)
            self.datamodel[key][1].append([timecode, value])
        # Release the lock
        finally:
            self.lock.release()
    
    # Periodically attempt to post saved data to the server
    def postdata(self):
        # Prep a 'failed posts' counter
        self.failedposts = 0
        self.timeout = 60*60  # 1 hour
        postlimit = 4
        # Initialise a database connection
        dbstruct = self.dbstructure()
        db = Database(self.CONFIG['dbfile'], dbstruct)
        self.log('WARN', 'POST DB INIT MSG: {}'.format(db.msg))
        # Now send some data to a locally installed version of frackbox
        url = self.CONFIG['posturl']
        # Generate an array of key names
        keys = ["timestamp","humandate"]
        for key in self.datamodel: keys.append(key)
        keys = json.dumps(keys)
        # Now periodically upload the data
        while True:
            # All is ok
            failed = False
            # Grab data to upload 
            qry = 'SELECT cid, csv FROM csvs WHERE uploaded = 0 LIMIT {}'.format(postlimit)
            rows = db.query(qry)
            self.log('WARN', 'DB for POST: {}'.format(qry))
            values = []
            cids = []
            postlimit += 2
            if postlimit >= 500: postlimit = 500
            # Prep for upload
            try:
                for row in rows:
                    cids.append(row[0])
                    values.append(row[1])
            except Exception as e:
                self.log('WARN', 'DB Error. rows = {}'.format(str(rows) ))
                db = Database(self.CONFIG['dbfile'], dbstruct) 
                failed = True
            # If we have data to post, then attempt to post it!
            if len(cids) > 0:
                jsonvalues = json.dumps(values)
                data = {
                    'serial':self.CONFIG['serial'],
                    'name':self.CONFIG['name'], 
                    'MAC':self.CONFIG['MAC'],
                    'jsonkeys': keys, 
                    'jsonvalues': jsonvalues
                }
                try:
                    poster = PostData()
                    resp = poster.send(url, data)
                    self.log('WARN', 'POSTer.msg: '+poster.msg )
                    self.log('WARN', 'POSTer resp: '+str(resp) )  
                except Exception as e:
                    resp = False
                    self.log('WARN', 'POST Error ')
                # Do we have a respose to read
                if resp is not False:
                    self.failedposts = 0
                    self.timepassed = 0
                    # We have posted data, but have errors from the server
                    if len(resp['errors']) > 0: 
                        self.log('WARN', 'POST ERRORS:'+str(resp['errors']) )
                    # All is fine
                    else:
                        # Update database as we have successfully uploaded all data
                        self.log('DEBUG', 'Sucessfully uploaded')
                        where = 'cid='+' OR cid='.join(map(str, cids))
                        qry = "UPDATE csvs SET uploaded=1 WHERE {}".format(where)
                        rows = db.query(qry)
                        #print(db.msg)
                        self.log('WARN', 'POST sucess DB: '+str(db.msg) ) 
                else:
                    failed = True
            # Start a counter if we have failed to upload
            if failed is True:
                # start a time to see how long we havent posted for
                if self.failedposts == 0: timerstart = self.counter 
                # Looks like we have a failed post
                self.failedposts = self.failedposts+1
                # If 1 hour has passed then restart
                self.timepassed = self.counter-timerstart
                if self.timepassed >= self.timeout:
                    self.log('WARN', 'NO NETWORK CONNECTION REBOOT: '+str(self.timeout))
                    subprocess.check_output("reboot", shell=True).decode("utf-8")
                self.log('WARN', 'UNABLE TO POST DATA [FailedPosts: {} timepassed: {} counter: {} postlimit: {}]'.format(self.failedposts, self.timepassed, self.counter, postlimit))
                postlimit = 2
            # And round again!
            self.healthcheck['postdata'] = self.counter 
            time.sleep(0.2)

    # Iterate through the data model and save data to: LogFile, GUI, Web
    # TODO: This is messy! Seperate data, display etc...
    def savedata(self):
        # Setup the database object
        dbstruct = self.dbstructure()
        self.db = Database(self.CONFIG['dbfile'], dbstruct)
        while True:
            # Block if the lock is already held by another process
            self.lock.acquire() 
            try:
                # Prep  web interface output
                thistime = time.strftime("%d/%m/%Y %H:%M:%S")+" Serial: "+self.CONFIG['serial']
                mystr = ""
                header = "timestamp, humandate, "
                hs = ''
                for key in self.datamodel:
                    values = ""
                    header = header+hs+key
                    for value in self.datamodel[key][1]: 
                        timecode = str(value[0]) 
                        val = str(value[1])
                        values = val+', '+values
                    mystr += '<div><b>'+key+':</b> '+values+'</div>'
                    hs = ', '
                # Prep the CSV output
                csvbuffer = ""
                rows = []
                for timecode in self.csvbuffer:
                    # Work out locsal time in human format
                    htimecode = timecode+self.CONFIG['timeadjustment']
                    ht = datetime.fromtimestamp( htimecode ).strftime('%Y-%m-%d %H:%M:%S')
                    line = str(timecode)+','+ht+','+','.join(self.csvbuffer[timecode])
                    # Prep data ready for database
                    rows.append([timecode, line, 0])
                    csvbuffer = csvbuffer+line+'\n'
                # save all the lovely new data to the database
                if len(rows) > 0: self.savetodb(rows)
                # Export to the web interface
                #self.setweb(header, csvbuffer)
                # Save data to the log file
                # TODO: Check the string isn't empty!!
                self.save.log(self.datapath, header, csvbuffer)
                # Now TODO: if the data has been saved, clear the buffer
                self.csvbuffer = OrderedDict([])
            finally:
                self.lock.release()
            self.healthcheck['savedata'] = self.counter 
            time.sleep(5)
    
    # Create the weblayout
    def setweb(self):
        # Setup the database object and query
        dbstruct = self.dbstructure()
        db = Database(self.CONFIG['dbfile'], dbstruct)
        qry = 'SELECT cid, uploaded, csv FROM csvs ORDER BY cid DESC LIMIT 400'
        # Build the header
        table = '<table><tr><th>'
        keys = ["cid","up","timestamp","humandate"]
        for key in self.datamodel:
            keys.append(key)
        keyheader = '</th><th>'.join(keys)
        table += keyheader+"</th></tr>"
        # Now loop through and keep updating the display
        while True:
            try:   
                # How many rows in the database
                num = db.query('SELECT count(*) FROM csvs') 
                uploaded = db.query('SELECT uploaded FROM csvs WHERE uploaded = 1;', 'count') 
                num = num[0][0]
                toupload = num-uploaded
                # Lets grab the latest data
                rows = db.query(qry)
                rowsstr = ''
                for row in rows:
                    vals = row[2].replace(',', '</td><td>')
                    rowsstr += '<tr><td>{}</td><td>{}</td><td>{}</td></tr>'.format(row[0], row[1], vals)
                # And build th final table
                body = table+rowsstr+'</table>'
                # Then build the heade string
                header = '<strong>Date:</strong> {} <strong>Device:</strong> {} <strong>ID:</strong> {} '.format(time.strftime("%d/%m/%Y %H:%M:%S"), self.CONFIG['name'], self.CONFIG['serial'] ) 
                header += '<strong>MAC:</strong> {} '.format(self.CONFIG['MAC'])
                header += '<hr />'
                header += '<strong>Rows:</strong> {} '.format(num)
                header += '<strong>Uploaded</strong> {} '.format(uploaded)
                header += '<strong>To upload: </strong> {} '.format(toupload)
                header += '<strong>Failed posts:</strong> {} '.format(self.failedposts)
                header += '<strong>Failed for:</strong> {} secs '.format(self.timepassed)
                if self.failedposts > 0:
                    header += '<strong>Reboot in:</strong> {} secs '.format(self.timeout-self.timepassed)
                header += '<br /><br />'
                body += "<h2>Config</h2><pre>{}</pre>".format(self.CONFIG)
                hc = ''
                for item in self.healthcheck:
                    hc += '{}: {} secs since last ran\n'.format(item, self.counter-self.healthcheck[item])
                body += "<h2>Thread Health</h2><pre>{}</pre>".format(hc)
                self.webserver.setcontent(header, body)
            except Exception as e:
                self.log('WARN', 'setweb(): '+str(e) )
            self.healthcheck['setweb'] = self.counter 
            time.sleep(3)

    # Save data to the database
    def savetodb(self, rows):
        data = {}
        data['fieldnames'] = ['timestamp', 'csv', 'uploaded']
        data['values'] = rows
        cids = self.db.create('csvs', data)

    # Used for application debugging
    def log(self, level, msg):
        datetime = time.strftime('%d/%m/%Y %H:%M:%S')
        msg = datetime+' '+msg
        if level == 'DEBUG':
            # Print to log  
            logging.debug(msg)
        elif level == 'INFO':
            # Print to log 
            logging.info(msg)
        elif level == 'WARN':
            # Print to log and console  
            logging.warning(msg)
    
    # Grab temperature / Humidity values
    def grabtemphumid(self):
        while True:
            try:
                sensor=AM2315()
                temp = sensor.temperature() 
                humid = sensor.humidity()
                #TODO: Dirty fix checking for zero values, sort with proper media check
                if temp != 999 and temp != 0.0:
                    self.temp = temp
                    self.newdata('XTemp', temp )
                if humid != 999:
                    self.humid = humid
                    self.newdata('XHumid', humid)
            except Exception as e:
                self.temp = 20
                self.newdata('XTemp', 'n/a')
                self.log('DEBUG', 'app.py | Exception | grabtemphumid() | '+str(e) )
            self.healthcheck['grabtemphumid'] = self.counter
            time.sleep(10)
   
    # Grab temperature / Humidity values
    def grabwinddir(self):
        # Read the wind direction
        while True:
            wind = winddir()
            compass = wind.grabdir()
            if compass is not False:
                self.newdata('winddir', compass)
            else:
                self.newdata('winddir', 'n/a')
                self.log('WARN', 'Wind dir is false:{}'.format(wind.msg))
            self.healthcheck['grabwinddir'] = self.counter 
            time.sleep(5)

    # Grab GPS data 
    def grabgps(self):
        ND = ND1000S() 
        while True:
            data = ND.grabdata()
            if data is not False:
                try:
                    info=json.loads(data)
                    self.log('DEBUG',"GOT GPS: "+data)
                    self.newdata('lat', info["lat"] )
                    self.newdata('lon', info["lon"] )
                    self.newdata('speed', info["speed"] )
                    self.newdata('alt', info["alt"] )
                except ValueError as e:
                    self.log('DEBUG', 'app.py | ValueError | GrabGPS() | '+str(data))
            else:
                    self.log('DEBUG', 'app.py | ValueError | GrabGPS() | '+ND.msg)
            self.healthcheck['grabgps'] = self.counter 
            time.sleep(6)
    
    # Grab ADC data from the ABelectronicsADC -> alphasense
    def grabalphasense(self):
        # Setup Alphasense calibration values
        calibration = self.CONFIG['alphasense']
        alphasense = Alphasense(calibration)
        # Now loop through a grab values
        while True: 
            # TODO: Replace with python3. The ADC library is provided as python2 so we use this subprocess hack to get the vars
            jsonstr = False
            try:
                jsonstr = subprocess.check_output("python2 /home/csk/csk/libraries/ABEadcPi.py", shell=True).decode("utf-8")
            except:
                self.log('WARN',"No alphasense ADC")
            try:
                info=json.loads(str(jsonstr))
                self.log('DEBUG',"Got ADC Info"+jsonstr)
                tc = int(time.time())
                self.newdata('PID', info["a1"], tc ) 
                self.newdata('NOwe3', int(info["a3"]), tc )
                self.newdata('NOae3', int(info["a2"]), tc )
                self.newdata('O3we2', int(info["a5"]), tc )
                self.newdata('O3ae2', int(info["a4"]), tc )
                self.newdata('NO2we1', int(info["a7"]), tc )
                self.newdata('NO2ae1', int(info["a6"]), tc )
                self.newdata('PT+', int(info["a8"]), tc )
                # Grab the external temperature
                temp = self.temp
                humidity = self.humid          
                # sensor, ae, we, temp 
                NO = alphasense.readppb('NO', info['a3'], info['a2'], temp) 
                #print(alphasense.msg)
                O3 = alphasense.readppb('O3', info['a5'], info['a4'], temp)
                #print(alphasense.msg)
                O3no2 = alphasense.readppb('O3no2', info['a5'], info['a4'], temp)
                #print(alphasense.msg)
                NO2 = alphasense.readppb('NO2', info['a7'], info['a6'], temp)  
                #print(alphasense.msg)
                PID = alphasense.readpidppm(info['a1'])
                #print(alphasense.msg)
                # Save the data
                self.newdata('NOppb', int(NO), tc )
                self.newdata('O3ppb', int(O3), tc )
                self.newdata('O3no2ppb', int(O3no2), tc )
                self.newdata('NO2ppb', int(NO2), tc )
                self.newdata('PIDppm', PID, tc )
            except ValueError:
                self.log('DEBUG', 'app.py | JsonError | grabadc() | '+str(jsonstr))
            self.healthcheck['grabalphasense'] = self.counter 
            time.sleep(4)

    # Grab RpiInfo
    def grabrpiinfo(self):
        while True: 
            jsonstr = subprocess.check_output("/home/csk/csk/libraries/RPiInfo.sh", shell=True).decode("utf-8")
            try:
                info=json.loads(jsonstr)
                self.log('DEBUG',"Got RaspberryPi Info"+jsonstr)
                self.CONFIG['MAC'] = info["MAC"] 
                self.newdata('CPU', info["tempc"] ) 
                self.newdata('Disk', info["disk%used"]+'/'+info["diskavailable"] )
                self.newdata('Load', info["load"] )
                #self.newdata(tc, 'deviceinfo', info["serial"] )
            except ValueError:
                self.log('DEBUG', 'app.py | ValueError | grabrpiinfo() | '+str(jsonstr))
            self.healthcheck['grabrpiinfo'] = self.counter 
            time.sleep(20)

    # Thread to check the network status
    def checknetwork(self):
        while True:
            # CHECK NETWORK / 3G DONGLE IS CONNECTED
            network = self.H3G.checkconnection()
            if network == True:
                self.log('DEBUG','Network OK')
                self.newdata('network', 'OK | {}'.format(self.failedposts))
            else:
                self.log('WARN','Network not connected')
                self.newdata('network', 'KO | {}'.format(self.failedposts))
            self.healthcheck['checknetwork'] = self.counter 
            time.sleep(20)

    # Thread to blink an led
    def redled(self):
        gpiopin=23
        onoff=0
        wiringpi2.pinMode(gpiopin,1)        # Set pin to 1 ( OUTPUT )
        wiringpi2.digitalWrite(gpiopin,1)   # Write 1 ( HIGH ) to pin 
        #wiringpi2.digitalRead(pin)         # Read pin 
        while True:
            time.sleep(0.25)
            onoff = not onoff
            wiringpi2.digitalWrite(gpiopin,onoff) # Write 1 ( HIGH ) to pin 

    # Thread to grab Barometer/Temp data from a: MPL115A2
    def barom(self):    
        while True:
            # read coefficients
            i2c.write(0x60, 0x00)
            print("a0_MSB:"+str( i2c.read(dev1) ) )
            #i2c.write(0x60, 0x00)
            #print('i2cX60: '+str( i2c.read(dev2) ) )
            time.sleep(2)
    
# Start grabbing sensors
GrabSensors()

##############################################################################
# RaspberryPi Pin Layout                                                     #
# TODO: Checkout alt pin numbering: http://makezine.com/projects/tutorial-raspberry-pi-gpio-pins-and-python
#============================================================================#
#        _____            ________                                           #
#        | pwr |          | SDcard |                                         #
#    ---------------------------------                                       #
#    |                  3v3 [ 1][ 2] | 5v                                    #       
#    |       GPIO0/SDA0-I2c [ 3][ 4] | 5v                                    #      
#    |       GPIO1/SCL0-I2c [ 5][ 6] | GND                                   #
#    |               GPCLK0 [ 7][ 8] | GPIO14/UART0-TXD                      #
#    |                  GND [ 9][10] | GPIO15/UART0-RXD                      #
#    |               GPIO17 [11][12] | GPIO18/PCM_CLK                        #
#    |               GPIO21 [13][14] | GND                                   #
#    |               GPIO22 [15][16] | GPIO23                                #
#    |                  3v3 [17][18] | GPIO24                                #
#    |     GPIO10/SPIO_MOSI [19][20] | GND                                   #
#    |      GPIO9/SPIO_MISO [21][22] | GPIO25                                #
#    |     GPIO11/SPIO_SCLK [23][24] | GPIO8/SPIO_CE0_N                      #
#    |                  GND [25][26] | GPIO7/SPIO_CE1_N                      #
# hdmi                               |___                                    #
#    |                               |vid|                                   #
#    |                               |---                                    #
#    |                               |___                                    #
#    |                               |aud|                                   #
#    |                               |---                                    #
#    |                               |                                       #
#    ---------------------------------                                       #
#      | eth |  | usb |                                                      #
#      -------  -------                                                      #
#                                                                            #
##############################################################################

