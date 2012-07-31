import socket
import sys
import thread
import time
import os
import urllib
import base64
from Tkinter import *

RETPORT=21454
host=str(sys.argv[1])
class App():
	def init(self):
		self.root = Tk()
		self.movs=[]
		self.cmovs=[]
		self.mylist=Listbox(self.root)
		self.scrollbar=Scrollbar(self.root)
		self.scrollbar.pack(side=RIGHT,fill=Y)
		self.mylist.pack(side=LEFT,fill=BOTH)
		self.mylist.configure(yscrollcommand=self.scrollbar.set)
		self.scrollbar.configure(command=self.mylist.yview)
		self.root.resizable(True,True)
		self.upd()
		self.root.mainloop()
	def upd(self):
		if(self.cmovs!=self.movs):
			print "ADDING!!!!!\n"
			cur=self.cmovs
			self.mylist.delete(0,END)
			self.movs=[]
			for i in cur:
				self.mylist.insert(END,i)
				self.movs.append(i)
		self.scrollbar.configure(command=self.mylist.yview)
		self.root.after(1000,self.upd)
	def askupd(self,nlst):
		self.cmovs=nlst
		
app=App()
def updgui():
	global app
	app.init()
def updateplaylist():
	global host
	s=socket.socket()
	s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	s.bind(("0.0.0.0",RETPORT))
	s.listen(5)
	while True:
		c,addr=s.accept()
		print "RETURNED!!!!!\n"
		msg=c.recv(10000)
		movs=msg.split('\n')
		app.askupd(movs)
		print msg


s=socket.socket()
port=int(sys.argv[2])
print "Connecting to ",host,port
s.connect((host,port))
thread.start_new_thread(updateplaylist,())
thread.start_new_thread(updgui,())
while True:
	msg=raw_input("Client >> ")
	s.send("BEGINCOM")
	msg=msg.split(' ')[0]
	if len(msg)>8:
		if(msg[0]=='\''):
			msg=msg[1:]
		if(msg[-1]=='\''):
			msg=msg[:-1]
	print msg
	if not os.path.isfile(msg):
		s.send(msg)
	else:
		inf="FILESENDINGBEGIN:"+os.path.basename(msg)+"BEGIN:"+str(base64.b64encode(open(msg).read()))+"FILESENDINGEND";
		print len(inf)
		s.send(inf)
	s.send("ENDCOM")
s.close()
