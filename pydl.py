#!/usr/bin/python3

# TODO: audit imports
import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.error import URLError, HTTPError
from lxml.html import parse
from contextlib import closing
import shutil, sys, re
import signal
import time

from threading import Thread
from queue import Queue
import collections

DEBUG = False
DEBUG_CLEAR = False

if DEBUG:
    from random import randint

"""
# TODO:

## FIX:
*  'URLs waiting...' displays negative queue size


## Project
* update gitlab
    * project description
    * roadmap
    * tickets
* update changelog
* merge branches
    * fix file names
    * do cleanup
* evaluate project against [phoemur/wgetter: Download utility written in python](https://github.com/phoemur/wgetter)
* move these notes into gitlab

## Features
* add command line options
    * download priority smallest files first
    * num threads per site
    * max total threads
    * debug toggles
        * debug messages
        * randomized test download file sizes
    * log toggle
    * output directory
    * input list
    * input file name
* add debug messages
* add log output
* thread timeouts
* signal handler
    * SIGKILL
    * SIGHUP
    * thread cleanup
* output order (downloaded first)
* file cleanup
* color output
* handle other sites 
    * use url description dictionary to add callbacks for links
"""

# TODO: finish signal handler (kill, hup)
# * needs to be more robust for threads
# * needs to clean up partially downloaded files
class MyError(Exception): 
    pass

def myHandler(sig, frame):
    raise MyError('Received signal ' + str(sig) +
                  ' on line ' + str(frame.f_lineno) +
                  ' in ' + frame.f_code.co_filename)    

signal.signal(signal.SIGINT, myHandler)
signal.signal(signal.SIGHUP, myHandler)

class Config:
    """ Configuration parameters 
    1. populate vars
    3. verify output directory -cwd(?)
    2. open input file -save descriptor
    """

    input_file_name = "infile"
    ifd = None                          # input file descriptor
    output_dir_path = "./"
    max_threads = 1

    def __init__(self):
        pass

class ScrapeFile:
    """ Class to get file
    """

    def __init__(self, input_url, download_path, file_id, report):
        #TODO: handle other site layouts (like sourceforge)
        purl = urllib.parse.urlparse(input_url)
        self.filename = purl.path.split('/')[-1]

        #build the download url 
        download_path_start = purl.scheme + "://" + purl.netloc + download_path + purl.path.split('/')[file_id]

        #TODO: add try block in caller
        self.download_path = purl.scheme + "://" + purl.netloc + self.follow(download_path_start)

        # set the output filename
        self.ofilename = self.download_path.split('/')[-1]

        # report class instance reference
        self.report = report

    def follow(self, url):
        """ Follow the url through redirects
        """
        while True:
            with closing(urllib.request.urlopen(url)) as stream:
                next = parse(stream).xpath("//meta[@http-equiv = 'refresh']/@content")
                if next:
                    url = next[0].split(";")[1].strip().replace("url=", "")
                    # temp hack return bc of known hop level
                    return url
                else:
                    return stream.geturl()

    def chunk_report(self, bytes_so_far, chunk_size, total_size):
        """ Report the latest downloaded file chunk
        """
        self.report.progressX[self.ofilename] = {"bytes_so_far": bytes_so_far, "total_size": total_size}


    def chunk_read(self, response, ofilename, chunk_size=8192, report_hook=None):
        total_size = int(response.headers["Content-Length"])
        bytes_so_far = 0
        data = []

        with open(ofilename,'wb') as ofd:
            while 1:
               chunk = response.read(chunk_size)

               if not chunk:
                  break

               bytes_so_far += len(chunk)

               if report_hook:
                  report_hook(bytes_so_far, chunk_size, total_size)

               ofd.write(chunk)

    def download(self):

        # just in case we need to look like a browser
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

        self.ofilename = self.download_path.split('/')[-1]
        req = urllib.request.Request(self.download_path, headers=hdr)
        response = urllib.request.urlopen(req)

        self.chunk_read(response, self.ofilename, report_hook=self.chunk_report)

    def test_thread(self):
        chunk_size = 8192
        inc = randint(0, 1024)

        total_size = 10240
        bytes_so_far = 0

        while bytes_so_far < total_size:
            time.sleep(.5)
            bytes_so_far += inc

            #compensate for random number overage
            if ( bytes_so_far > total_size):
                bytes_so_far = total_size

            self.chunk_report(bytes_so_far, chunk_size, total_size)


class ThreadProc(Thread):

    def __init__(self, urlq, tq, dl_site_info, report):
        Thread.__init__(self)
        self.urlq = urlq
        self.tq = tq
        self.dl_site_info = dl_site_info
        self.report = report

    def run(self):
        try:
            url = self.urlq.get()
            while True:
                if self.urlq == None:
                    break;

                # setup download_path link portion
                download_path = None
                id_pos = None

                # grab the base download url based on the patterns provided
                for key, value in dl_site_info.items():
                    if ( key in url ):
                        download_path = value["download_path"]
                        # grab the file id position from the template
                        id_pos = value["id_pos"]

                # TODO: needs error handling -exit bad
                if( download_path == None ):
                    print("ERROR: base url of website not configured")
                    # TODO: should probably just continue here
                    sys.exit(1)

                # create object and do work
                try:
                    o = ScrapeFile(url, download_path, id_pos, report)
                    report.progressX[o.ofilename] = {"bytes_so_far": 0, "total_size": 0}
                    if DEBUG:
                        o.test_thread()
                    else:
                        o.download()
                    self.tq.get()
                    self.urlq.task_done()
                    break;
                except urllib.error.HTTPError as err:
                    print("ERROR: %s | HTTPError: %s" % (url, err))
                    continue

        except MyError as err:
            print("\n" + "** signal caught: %s **\n" % err)
            exit(1)

        #self.tq.task_done()


class Report:
    def __init__(self):
        self.progressX = collections.OrderedDict()

    def print_progress(self):
        if not DEBUG_CLEAR:
            sys.stdout.write('\033[2J\033[H') #clear screen
            sys.stdout.flush()

        for filename, item in self.progressX.items():
            #FIX: why do i need to test for > 0 ??
            if(item["total_size"] > 0):
                percent = float(item["bytes_so_far"] / item["total_size"])
                bar = ('=' * int(percent * 20)).ljust(20)
                percent = int(percent * 100)
                sys.stdout.write("%s [%s] %s%% @ %sMb of %sMb\n" % 
                                 (filename, bar, percent, int(item["bytes_so_far"] / 1024 / 1024), int(item["total_size"] / 1024 / 1024)))
                sys.stdout.flush()


#################### Main
if __name__ == '__main__':
    """
    1. create params object and populate configuration
    1a. use threads...
    2. loop through input file
    3. download file from scrape
    """

    # TODO: add argv handling
    # * add output directory
    # configurables 
    # TODO: This is kind of dumb -probably need another way to do this for url patterns
    dl_site_info = {
        # uses  format: http://site-A.com/download/13522
        "site-A": {"download_path": "/download/", "id_pos": -2}, 
        # uses format: http://site-B.com/downloadfile/5710
        "site-B": {"download_path": "/downloadfile/", "id_pos": -1}, 
        # uses format: https://sourceforge.net/projects/freemind/files/latest/download?source=directory
        # TODO: needs it's own scraper
        "sourceforge": {"download_path": "/projects/", "id_pos": -1} 
                   }
    input_file = "dl.input"

    # read input data into array
    inf_arr = []
    urlq = Queue()
    #progress = collections.OrderedDict()

    try:
        with open(input_file) as ifd:
            for line in ifd:
                #if ("#" in line):
                if ( ("#" in line) or (line == '\n') ):
                    continue
                inf_arr.append(line.rstrip('\n'))
                urlq.put(line.rstrip('\n'))
    except EnvironmentError as err:
        print("Error: problem with input file | %s" % err)
        sys.exit(1)

    # report class
    report = Report()

    # thread count queue
    tq = Queue()

    ########### process loop start
    max_threads = 5

    if DEBUG:
        print("creating threads | urlq.qsize(): %s" % (urlq.qsize()))
        time.sleep(1)

    while not urlq.empty():

        for i in range(max_threads):
            if not urlq.empty() and (tq.qsize() < max_threads):
                # start threads
                # TODO: catch exceptions and continue download if possible
                t=ThreadProc(urlq, tq, dl_site_info, report)
                tq.put(i)
                t.setDaemon(True)
                t.start()

                if DEBUG:
                    print("creating thread: %d | tq.qsize(): %d" % (i,tq.qsize()))
                    time.sleep(1.0)


        #while any(i.is_alive() for i in workers):
        while not tq.empty():
            report.print_progress()
            print("URLs waiting in queue: %s | Number files downloading: %s" % ((urlq.qsize()), tq.qsize()))
            time.sleep(0.1)

            # add more threads if something has finished
            if not  urlq.empty():
                if tq.qsize() < max_threads:
                    break

    # print last report if needed
    report.print_progress()

    #tq.join()
    ########### process loop end
