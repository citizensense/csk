#!/usr/bin/python3
import threading, subprocess
import cherrypy as http

class CherryPyWebServer:
    
    def __init__(self, globalconfig, localconfig):
        self.globalconfig = globalconfig
        self.localconfig = localconfig
        self.server = Rest()
        thread = threading.Thread(target=self.serverthread)
        thread.start()

    def serverthread(self):
        http.config.update(self.globalconfig)
        http.quickstart( self.server, '/', self.localconfig )   

    def setcontent(self, body, log):
        self.server.setcontent(body, log)

class Rest:
    
    def __init__(self):
        self.body = "Started webserver"
        self.log = "Started..."

    def setcontent(self, body, log):
        self.body = body
        self.log = log

    @http.expose
    def index(self):
        SYSTEM = self.systeminfo()
        BODY = self.body
        LOG = self.log
        return """
        <html>
        <head>
            <meta http-equiv="refresh" content=20; URL="/">
            <style>
                #leftcol{
                    float:left;
                    width:49%;
                    border-right:1px solid #ccc;
                }
                #rightcol{
                    float:right;
                    width:49%;
                    border-left:1px solid #ccc;
                }
                .padd{
                    margin:10px;
                }
                th, td{
                    font-size:80%;
                    vertical-align: text-top;
                    font-family:"Lucida Console", Monaco, monospace;
                    overflow:hidden;
                    border:1px solid #ccc;
                    white-space: nowrap;   
                }
            </style>
        </head>
        <body class="padd">
        """+BODY+"""

        <div>
            """+LOG+"""
        </div>
        <div>
            <h2>SYSTEM INFO</h2>
            """+SYSTEM+"""
        </div>
        </body>
        </html>

        </html>
        """

    @http.expose
    def posted(self, uuid):
        return """
        <html><body>
        <p>%s</p>
        </body>
        </html>
        """ % uuid
    
    def systeminfo(self):
        # Show i2c
        try:
            i2c = subprocess.check_output("i2cdetect -y 1", shell=True).decode('utf-8')
        except:
            i2c = 'i2c: Cant connect'
        # Show processes
        try:
            ps = subprocess.check_output("ps aux | grep app", shell=True).decode('utf-8')
        except:
            ps = 'ps: Failed to show output'
        # Show processes
        try:
            ps = subprocess.check_output("ps aux | grep app", shell=True).decode('utf-8')
        except:
            ps = 'ps: Failed to show output'
        # Show network
        try:
            ipa = subprocess.check_output("ip a", shell=True).decode('utf-8')
        except:
            ipa = 'ip: Failed to load ip info'
        # Show systemctl status
        try:
            sysctl = subprocess.check_output("systemctl status cskboot", shell=True).decode('utf-8')
        except:
            sysctl = 'sysctl: Failed to load service info'
        # Buildthe output string
        msg = '<h3>I2C</h3><pre>{}</pre>'.format(i2c)
        msg += '<h3>ps aux | grep app</h3><pre>{}</pre>'.format(ps)
        msg += '<h3>ip a</h3><pre>{}</pre>'.format(ipa)
        msg += '<h3>systenctl status cskboot</h3><pre>{}</pre>'.format(sysctl)
        # Show systemctl status
        return msg

if __name__ == "__main__":
    import time
    globalconfig = {
        'server.socket_host':"0.0.0.0", 
        'server.socket_port':80
    } 
    localconfig = {'/': {'tools.staticdir.root': '../public'}}
    webserver = CherryPyWebServer(globalconfig, localconfig) 
    n=0
    while True:
        time.sleep(5)
        webserver.setcontent(str(n)+'Content', 'Has Been set')
        n = n+1

