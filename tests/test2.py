#!/usr/bin/python3

import urllib.request
import time

hosts = ["http://yahoo.com",
         "http://amazon.com",
         "http://google.com",
         "http://apple.com",
         "http://ibm.com",
         "http://yahoo.com"]
         #"http://amazon.com",
         #"http://google.com",
         #"http://apple.com",
         #"http://ibm.com",

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

hdr = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' 
      }

start = time.time()
#grabs urls of hosts and prints first 1024 bytes of page
for host in hosts:
  print( host +'\n')
  req = urllib.request.Request(host, headers=hdr)
  url = urllib.request.urlopen(req)
  #print url.read(1024)
  url.read(1024)
  #time.sleep(1)

print("Elapsed Time: %s" % (time.time() - start))
