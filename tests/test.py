#!/usr/bin/python3

import urllib.parse
import sys

download_suffex = "download"

url = "http://txmovie.in/item/2800/fight-club-1999"
purl = urllib.parse.urlparse(url)

filename = purl.path.split('/')[-1]

path = purl.netloc+"/download/"+filename

print(filename)
print("http://"+path)

#-----------------------------------------------------------------
print("---------------------------------------------------------")

import threading
import datetime

class ThreadClass(threading.Thread):
  def run(self):
    now = datetime.datetime.now()
    print("%s says Hello World at time: %s" % (self.getName(), now))

for i in range(2):
  t = ThreadClass()
  t.start()

#-----------------------------------------------------------------
print("---------------------------------------------------------")

#import urllib2
import urllib
import urllib.request
import time


#hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",

hosts = [ "http://google.com",
         "http://amazon.com",
         "http://yahoo.com",
         "http://ibm.com",
         "http://apple.com"]

hdr = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }

start = time.time()
#grabs urls of hosts and prints first 1024 bytes of page
for host in hosts:
  print(host +'\n')
  #url = urllib2.urlopen(host)
  req = urllib.request.Request(host, headers=hdr)
  url = urllib.request.urlopen(req)
  #print(url.read(1024))
  url.read(1024)

print("Elapsed Time: %s" % (time.time() - start))


#-----------------------------------------------------------------
print("---------------------------------------------------------")

import queue
import threading
import urllib
import time

hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
"http://ibm.com", "http://apple.com"]

hdr = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' }

queue = queue.Queue()

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
          #grabs host from queue
          host = self.queue.get()
          req = urllib.request.Request(host, headers=hdr)

          #grabs urls of hosts and prints first 1024 bytes of page
          url = urllib.request.urlopen(req)
          #print url.read(1024)
          url.read(1024)

          #signals to queue job is done
          self.queue.task_done()

start = time.time()
def main():

    #spawn a pool of threads, and pass them queue instance
    for i in range(5):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()

        #populate queue with data
        for host in hosts:
            queue.put(host)

    #wait on the queue until everything has been processed
    queue.join()

main()
print("Elapsed Time: %s" % (time.time() - start))

#-----------------------------------------------------------------
print("---------------------------------------------------------")
