import socket
import sys
import thread
import time
def updateplaylist(s,tmp):
	while True:
		s.send("getplaylist")
		msg=s.recv(1000000)
		print msg
		time.sleep(2)

s=socket.socket()
host=str(sys.argv[1])
port=int(sys.argv[2])
print "Connecting to ",host,port
s.connect((host,port))
thread.start_new_thread(updateplaylist,(s,""));

while True:
	msg=raw_input("Client >> ")
	s.send(msg)

