#!/usr/bin/python           # This is server.py file
 
import socket               # Import socket module
from  thread import *
import sys
import re
import os
import urllib
RETPORT=21454
songlist=[]
namelist=[]
down=0
iplist=[]
def sendupdatedlist():
	global iplist
	global namelist
	songstr=""
	cur=1;
	for i in namelist:
		songstr+=str(cur)
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
	while(1):
		while(len(songlist)==0):
			continue
		print "playing ",songlist[0]
		os.system("mplayer -vo null "+songlist[0])
		songlist=songlist[1:]
		namelist=namelist[1:]
		sendupdatedlist()

def download_youtube(link):
	os.system("python youtube-dl "+link)
	if(len(re.findall("http",link))==0):
		link="http://"+link
	nl=re.findall("span id=\"eow-title\".*?title=\"(.*?)\"",urllib.urlopen(link).read())

	if(len(nl)==0):
		namelist.append("nameless")
	else:
	 	namelist.append(nl[0])
	print "NAME=====================================+++>" +nl[0]
	link+="&"
	fname=re.findall("\?v=(.*?)\&",link)[0]
	songlist.append(fname+".mp4")

def download(link,tmp):
	global songlist
	global namelist
	global down
	if(len(re.findall("cache",os.getcwd()))==0):
		os.chdir("cache_folder")
	while(down>=5):
		continue
	down+=1
	download_youtube(link)
	down-=1
	sendupdatedlist()
def handler(clientsock,addr,s):
	global iplist
	iplist.append(addr)
	while 1:
		data=clientsock.recv(1024)
		start_new_thread(download,(data,0))
		if not data:
			break
	print "broken"
	iplist[:]=[x for x in iplist if x!=addr]
	clientsock.close()

s = socket.socket()         # Create a socket object
host = str(sys.argv[1])     # Get local machine name
port = int(sys.argv[2])     # Reserve a port for your service.
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
