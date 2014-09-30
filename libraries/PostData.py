#!/usr/bin/python3
import urllib.request
import urllib.parse

class PostData:

    # Simple method to post some data
    def send(self, url, data):
        data = urllib.parse.urlencode(data)
        data = data.encode('utf-8')
        request = urllib.request.Request(url)
        # adding charset parameter to the Content-Type header.
        request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
        f = urllib.request.urlopen(request, data)
        print(f.read().decode('utf-8'))

if __name__ == "__main__":
    import time
    # Initialise the object
    poster = PostData()
    # Now send some data to a locally installed version of frackbox
    url = 'http://192.168.1.100:8787/api'
    while True:
        data = {'header': 1, 'csv': 2}
        poster.send(url, data)
        timer.sleep(5)

