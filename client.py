import socket
import sys
import thread
import time
import os
import urllib
import base64
from Tkinter import *
import threading
import re
import youtubedl
import readline
	

COMMANDS=['extra']

RE_SPACE = re.compile('.*\s+$', re.M)
class Completer(object):

    def _listdir(self, root):
        "List directory 'root' appending the path separator to subdirs."
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res

    def _complete_path(self, path=None):
        "Perform completion of filesystem path."
        if not path:
            return self._listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [os.path.join(dirname, p)
                for p in self._listdir(tmp) if p.startswith(rest)]
        # more than one match, or single match which does not exist (typo)
        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self._listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def complete_extra(self, args):
        "Completions for the 'extra' command."
        if not args:
            return self._complete_path('.')
        # treat the last arg as a path and complete it
        return self._complete_path(args[-1])

    def complete(self, text, state):
        "Generic readline completion entry point."
        buffer = readline.get_line_buffer()
        line = readline.get_line_buffer().split()
        # show all commands
        if not line:
            return [c + ' ' for c in COMMANDS][state]
        # account for last argument ending in a space
	line.insert(0,"extra")
        if RE_SPACE.match(buffer):
            line.append('')
        # resolve command to the implementation function
        cmd = line[0].strip()
        if cmd in COMMANDS:
            impl = getattr(self, 'complete_extra' )
            args = line[1:]
            if args:
                return (impl(args) + [None])[state]
            return [cmd + ' '][state]
        results = [c + ' ' for c in COMMANDS if c.startswith(cmd)] + [None]
        return results[state]

comp=Completer()
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(comp.complete)

RETPORT=21455
host=str(sys.argv[1])
sfname=[]
namelist=[]

s=socket.socket()
listempty=threading.Semaphore(value=1)
listempty.acquire()
down=0
sock=socket.socket()
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

def uploadsongs():
	global sfname
	global namelist
	while True:
		if len(sfname)!=0:
			listempty.release()
		listempty.acquire()
		msg=sfname[0]
		inf="FILESENDINGBEGIN:"+os.path.basename(namelist[0])+"BEGIN:"+str(base64.b64encode(open(msg).read()))+"FILESENDINGEND";
		s.send("BEGINCOM")
		s.send(inf)
		s.send("ENDCOM")
		namelist=namelist[1:]
		sfname=sfname[1:]
		if len(sfname)!=0:
			listempty.release()
		else:
			listempty.acquire();

def addsong(fname,sname):
	global sfname
	global namelist
	sfname.append(fname)
	namelist.append(sname)
	listempty.release()
def download_youtube(link):
	global sem
	if(len(link)==0):
		return;
#	print "DOWNLOADING       " + link
#	os.system("python youtube-dl "+link)
	fname=re.findall("\?v=(.*?)\&",link+"&")[0]
	print os.path.join(os.getcwd(),fname+".mp4")
	if not os.path.isfile(os.getcwd()+"/"+fname+".mp4") :
		fd=youtubedl.FileDownloader({"outtmpl":u'%(id)s.%(ext)s'})
		for e in youtubedl.gen_extractors():
			fd.add_info_extractor(e)
		fd.download([link])
	if(len(re.findall("http",link))==0):
		link="http://"+link
	nl=re.findall("span id=\"eow-title\".*?title=\"(.*?)\"",urllib.urlopen(link).read())
	if(len(nl)==0): 
		nl="nameless"
	else:
	 	nl=nl[0]
#	print "NAME=====================================+++>" +nl[0]
	addsong(os.path.join(os.getcwd(),fname+".mp4"),nl)

def download(link,tmp):
	global songlist
	global namelist
	global down
	global sem
	print len(link)
	if(len(re.findall("cache",os.getcwd()))==0):
		os.chdir("cache_folder")
	while(down>=5):
		continue
	down+=1
	if len(re.findall("youtube",link))!=0:
		download_youtube(link)
	elif(len(link)>4):
		if(link[-4:]==".mp3"  and len(re.findall(link,"www"))!=0):
			loc=urllib.urlretrieve(link)[0]
			move(loc,"./")
			addsong((str(os.getcwd())+os.path.basename(loc)),os.path.basename(loc))
		else:
			if(os.path.isfile(link)):
				addsong(link,link)
	down-=1

def updateplaylist():
	global host
	global sock
#	s2=socket.socket()
#	s2.bind(("0.0.0.0",RETPORT))
	sock.listen(5)
	while True:
		c,addr=sock.accept()
		print "RETURNED!!!!!\n"
		msg=c.recv(10000)
		movs=msg.split('\n')
		app.askupd(movs)
		print msg


port=int(sys.argv[2])
print "Connecting to ",host,port
s.connect((host,port))
thread.start_new_thread(updgui,())
thread.start_new_thread(uploadsongs,())

s.send("BEGINCOM");
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('',0))
RETPORT=sock.getsockname()[1]
print "RETPORT!!!!!      ",RETPORT
s.send(str(sock.getsockname()[1]))
s.send("ENDCOM");
thread.start_new_thread(updateplaylist,())
while True:
	msg=raw_input("Client >> ")
	msg=msg.rstrip()
	msg=msg.lstrip()
	if len(msg)>8:
		if(msg[0]=='\''):
			msg=msg[1:]
		if(msg[-1]=='\''):
			msg=msg[:-1]
	print msg
#	if not os.path.isfile(msg):
#		s.send(msg)
#	else:
	thread.start_new_thread(download,(msg,1234))
#		inf="FILESENDINGBEGIN:"+os.path.basename(msg)+"BEGIN:"+str(base64.b64encode(open(msg).read()))+"FILESENDINGEND";
#		inf="FILESENDINGBEGIN:"+os.path.basename(msg)+"BEGIN:"+str(open(msg).read())+"FILESENDINGEND";
#	print len(inf)
s.close()
