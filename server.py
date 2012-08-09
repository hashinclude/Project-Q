#!/usr/bin/python           # This is server.py file
 
import socket               # Import socket module
from  thread import *
import sys
import re
import os
import urllib
import youtubedl
from shutil import *
import base64
import threading
RETPORT=21454
songlist=[]
namelist=[]
down=0
iplist=[]
sem=threading.Semaphore(value=1)
sem.acquire()
def recvbigdata(clientsock):
	ret=""
	cstr=""
	while(True):
		cstr=clientsock.recv(100)
#		print cstr
#		print "\n\n"
		if(len(cstr)>=8):
#			print "=============>"
#			print cstr[:8]
#			print cstr[:8]=="BEGINCOM"
			if(cstr[:8]=="BEGINCOM"):
				ret=cstr[8:]
				break
	while True:
		cstr=clientsock.recv(1024)
		if(len(cstr)>=6):
			if(cstr[-6:]=="ENDCOM"):
				ret+=cstr[:-6]
				return ret
		ret+=cstr
#		print ret
		
def sendupdatedlist():
	global iplist
	global namelist
	songstr=""
	cur=1;
	for i in namelist:
		songstr+=str(cur)
		cur+=1
		songstr+=". "
		songstr+=i
		songstr+="\n"
	for i in iplist:
		s=socket.socket()
		print "UPDATING "+str(i)
		s.connect((i[0],RETPORT))
		s.send(str(songstr))
		s.close()

def playlist():
	global songlist
	global namelist
	global sem
	while(1):
		if(len(songlist)!=0):
			sem.release()
		sem.acquire()
		print "playing ",songlist[0]
		os.system("mplayer \""+songlist[0]+"\"")
		songlist=songlist[1:]
		namelist=namelist[1:]
		sendupdatedlist()
		if(len(songlist)==0):
			sem.acquire()

def download_youtube(link):
	global sem
	if(len(link)==0):
		return;
#	print "DOWNLOADING       " + link
#	os.system("python youtube-dl "+link)
	fname=re.findall("\?v=(.*?)\&",link+"&")[0]
	print os.getcwd()+fname+".mp4"
	if not os.path.isfile(os.getcwd()+"/"+fname+".mp4") :
		fd=youtubedl.FileDownloader({"outtmpl":u'%(id)s.%(ext)s'})
		for e in youtubedl.gen_extractors():
			fd.add_info_extractor(e)
		fd.download([link])
	if(len(re.findall("http",link))==0):
		link="http://"+link
	nl=re.findall("span id=\"eow-title\".*?title=\"(.*?)\"",urllib.urlopen(link).read())

	if(len(nl)==0):
		namelist.append("nameless")
	else:
	 	namelist.append(nl[0])
#	print "NAME=====================================+++>" +nl[0]
	songlist.append(fname+".mp4")
	sem.release()

def download(link,tmp):
	global songlist
	global namelist
	global down
	global sem
	print len(link)
	if(link!="INISEND"):
		if(len(re.findall("cache",os.getcwd()))==0):
			os.chdir("cache_folder")
		while(down>=5):
			continue
		down+=1
		if len(re.findall("youtube",link))!=0:
			download_youtube(link)
		elif(len(link)>4):
			if(link[-4:]==".mp3" and len(re.findall("FILESENDINGBEGIN",link))==0):
				loc=urllib.urlretrieve(link)[0]
				move(loc,"./")
				songlist.append(os.path.basename(loc))
				namelist.append(os.path.basename(loc))
				sem.release()
			else:
				lst=re.findall("FILESENDINGBEGIN:(.*?)BEGIN:(.*?)FILESENDINGEND",link)
				if(len(lst)!=0):
					lst=lst[0]
					x=open(lst[0],"w")
					x.write(base64.b64decode(lst[1]))
					x.write(lst[1])
					x.close()
					songlist.append(lst[0])
					namelist.append(lst[0])
					sem.release()
		down-=1
	sendupdatedlist()
def handler(clientsock,addr,s):
	global iplist
	iplist.append(addr)
	data="INISEND"
	while 1:
		start_new_thread(download,(data,0))
		data=recvbigdata(clientsock)
		if not data:
			break
	print "broken"
	iplist[:]=[x for x in iplist if x!=addr]
	clientsock.close()

s = socket.socket()         # Create a socket object

host = str(sys.argv[1])     # Get local machine name
port = int(sys.argv[2])     # Reserve a port for your service.
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind((host, port))        # Bind to the port
s.listen(5)                 # Now wait for client connection.

start_new_thread(playlist,())
print 'Server started!'
while True:
	print 'Waiting for clients...'
	c, addr = s.accept()     # Establish connection with client.
	print 'Got connection from', addr
	start_new_thread(handler,(c,addr,s))
s.close
