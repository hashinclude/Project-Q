from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
import socket
from settings_server import *
import os
from thread import *
import threading
import cgi
import time
import mplayer

namelist=[]
songlist=[]
sem=threading.Lock()
def playlist():
	global songlist
	global namelist,songinfo
	global sem, p
	while(1):
		if(len(songlist)==0):
			sem.acquire()
			sem.acquire()
		print songlist[0]
		p.loadfile(songlist[0]);
		try:
			print open(songlist[0]+".info.json").read()
		except:
			print "No Info File"
		time.sleep(1)
		while(p.time_pos!=None):
			time.sleep(1)
		print "DEAD"
		songlist=songlist[1:]
		namelist=namelist[1:]
class FormPage(Resource):
    def render_GET(self, request):
	    global CACHEFOLDER
	    print request.prepath
	    request.setResponseCode(200)
	    if(request.prepath==["getplaylist"]):
	          ret="<table>"
	    	  for i in namelist:
	    		ret+="<tr><td>%s</td></tr>"%i
	   	  ret+="</table>"
		  print ret
		  return ret
	    elif(request.prepath==["chkex"]):
		    fname=os.path.basename(request.args['filename'][0])
		    fname=os.path.join(CACHEFOLDER,fname)
		    if(os.path.isfile(fname)):
			    return "found"
		    else:
			    return "notfound"
    def render_POST(self, request):
	  if(request.prepath==["uploadsong"]):
		  self.headers=request.getAllHeaders()
		  img=cgi.FieldStorage(fp=request.content, headers=self.headers, \
				              environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['content-type'], })

		  fname=os.path.basename(img['upfile'].filename)
		  fname=os.path.join(CACHEFOLDER,fname)
		  if(os.path.isfile(fname)):
			  print "already exists"
		  else:
			  fp=open(fname,"wb")
			  fp.write(img['upfile'].value)
			  fp.close()
		  fname=os.path.basename(img['filejson'].filename)
		  fname=os.path.join(CACHEFOLDER,fname)
		  if(os.path.isfile(fname)):
			  print "already exists"
		  else:
			  fp=open(fname,"wb")
			  fp.write(img['filejson'].value)
			  fp.close()
	          songlist.append(fname) 
	    	  print len(songlist)
	          try:
			  namelist.append(self.headers['songname'])
		  except:
			  namelist.append(fname)

		  if(sem.locked_lock()):
			  sem.release()
		  return "<meta http-equiv=\"REFRESH\" content=\"0;url=http://localhost:8881\">"
def keepreplying():
	global recvsock,sendsock,p,UDPREPLYPORT
	while(True):
		data,addr=recvsock.recvfrom(1024)
		sendsock.sendto("%s::%s::%s"%(p.filename,str(p.time_pos),str(p.paused)),(addr[0],UDPREPLYPORT))


p=mplayer.Player()		
root = Resource()
root.putChild("uploadsong", FormPage())
root.putChild("getplaylist", FormPage())
root.putChild("chkex", FormPage())
recvsock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
recvsock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
recvsock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)	
recvsock.bind(("127.0.0.1",UDPLISTENPORT))
sendsock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
start_new_thread(keepreplying,())
factory = Site(root)
reactor.listenTCP(HOSTPORT, factory)
start_new_thread(playlist,())
reactor.run()

