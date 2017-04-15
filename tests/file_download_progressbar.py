# source:
# http://stackoverflow.com/questions/5783517/downloading-progress-bar-urllib2-python

import urllib.request
import sys

'''
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
'''

def chunk_report(bytes_so_far, chunk_size, total_size):
   percent = float(bytes_so_far) / total_size
   percent = round(percent*100, 2)
   sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % 
       (bytes_so_far, total_size, percent))

   if bytes_so_far >= total_size:
      sys.stdout.write('\n')

def chunk_read(response, ofilename, chunk_size=8192, report_hook=None):
   #total_size = response.info().getheader('Content-Length').strip()
   total_size = response.headers["Content-Length"]
   #print("total_size: %d" % int(total_size))
   total_size = int(total_size)
   bytes_so_far = 0
   data = []

   ofd=open(ofilename,'wb')

   while 1:
      chunk = response.read(chunk_size)
      bytes_so_far += len(chunk)

      if not chunk:
         break

      data += chunk
      if report_hook:
         report_hook(bytes_so_far, chunk_size, total_size)

      ofd.write(chunk)

   return "".join(data)

if __name__ == '__main__':
   url = "http://txmovie.in/item/6804/the-neighbor-2016"+"(720p-bluray).mp4"
   file_name = url.split('/')[-1]
   durl = "http://txmovie.in/m2/"+file_name

   response = urllib.request.urlopen(durl);
   chunk_read(response, file_name, report_hook=chunk_report)
