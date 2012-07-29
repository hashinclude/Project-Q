#!/usr/bin/python           # This is server.py file
 
import socket               # Import socket module
from  thread import *
import sys
import re
import os

songlist=[]
down=0
def playlist():
	global songlist
	while(1):
		while(len(songlist)==0):
			continue
		print "playing ",songlist[0]
		os.system("mplayer -vo null "+songlist[0])
		songlist=songlist[1:]

def download(link,tmp):
	global songlist
	global down
	if(len(re.findall("cache",os.getcwd()))==0):
		os.chdir("cache_folder")
	while(down>=5):
		continue
	down+=1
	os.system("python youtube-dl "+link)
	down-=1
	link+="&"
	fname=re.findall("\?v=(.*?)\&",link)[0]
	songlist.append(fname+".mp4")
def handler(clientsock,addr,s):
	while 1:
		data=clientsock.recv(1024)
		if data=="getplaylist":
			s.send(str(songlist))
			break
		start_new_thread(download,(data,0))
		if not data:
			break
	print "broken"
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
