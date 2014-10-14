#!/usr/bin/python3
import urllib.request
import urllib.parse
import json

class PostData:

    # Simple method to post some data
    def send(self, url, data):
        self.msg = 'Posting data'
        data = urllib.parse.urlencode(data)
        data = data.encode('utf-8')
        request = urllib.request.Request(url)
        # adding charset parameter to the Content-Type header.
        request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        try:
            f = urllib.request.urlopen(request, data)
            #f2 = urllib2.urlopen(f, timeout=10)
        except Exception as e:
            self.msg += 'POST Error: '+str(e)
            return False
        response = f.read().decode('utf-8')
        try:
            return json.loads(response)            
        except Exception as e:
            self.msg += 'Json Response Error: '+str(e) 
            return False

if __name__ == "__main__":
    import time
    # Initialise the object
    poster = PostData()
    # Now send some data to a locally installed version of frackbox
    url = 'http://192.168.1.100:8787/api'
    url = 'http://frackbox.citizensense.net/api'
    print('Test POST to: {}'.format(url))
    while True:
        data = {'header': 1, 'csv': 2}
        resp = poster.send(url, data)
        print(str(resp))
        print(poster.msg)
        time.sleep(5)

