from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import os
from thread import *
import threading
import cgi
import time
namelist=[]
songlist=[]
sem=threading.Semaphore(value=1)
sem.acquire()
def playlist():
	global songlist
	global namelist
	global sem
	while(1):
		if(len(songlist)==0):
			sem.acquire()
		if(len(songlist)!=0):
			sem.release()
		sem.acquire()
		print songlist[0]
		os.system("mplayer -really-quiet \""+songlist[0]+"\"")
		songlist=songlist[1:]
		namelist=namelist[1:]
#		sendupdatedlist()
		if(len(songlist)==0):
			sem.acquire()
class FormPage(Resource):
    def render_GET(self, request):
	    print request
	    request.setResponseCode(200)
    def render_POST(self, request):
	  print request
	  self.headers=request.getAllHeaders()
	  img=cgi.FieldStorage(fp=request.content, headers=self.headers, \
			              environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['content-type'], })
	  fname=os.path.basename(img['upfile'].filename)
	  fname=os.path.join("cache_folder",fname)

	  if(os.path.isfile(fname)==True):
		  print "ALREADY EXISTS"
	  else:
		  fp=open(fname,"wb")
		  fp.write(img['upfile'].value)
		  fp.close()
          songlist.append(fname)
	  namelist.append(fname)
	  sem.release()

root = Resource()
root.putChild("uploadsong", FormPage())
root.putChild("updplay", FormPage())
factory = Site(root)
reactor.listenTCP(8880, factory)
start_new_thread(playlist,())
reactor.run()

