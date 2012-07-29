import socket
import sys
import thread
import time
RETPORT=21454
host=str(sys.argv[1])
def updateplaylist():
	global host
	s=socket.socket()
	s.bind((host,RETPORT))
	s.listen(5)
	while True:
		c,addr=s.accept()
		print "RETURNED!!!!!\n"
		msg=c.recv(10000)
		print msg

s=socket.socket()
port=int(sys.argv[2])
print "Connecting to ",host,port
s.connect((host,port))
thread.start_new_thread(updateplaylist,());

while True:
	msg=raw_input("Client >> ")
	s.send(msg)
s.close()
