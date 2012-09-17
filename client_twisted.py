import socket
import sys
import thread
import time
import os
import urllib
import base64
import threading
import re
import youtubedl
import readline
import urllib2,urllib
import itertools
import mimetools
import mimetypes
import shutil
import mplayer
from settings_client import *
from cStringIO import StringIO
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from thread import *


	

COMMANDS=['extra']
curplist=""

RE_SPACE = re.compile('.*\s+$', re.M)
down=0
class MultiPartForm(object):
    """Accumulate the data to be used when posting a form."""

    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = mimetools.choose_boundary()
        return
    
    def get_content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def add_field(self, name, value):
        """Add a simple field to the form data."""
        self.form_fields.append((name, value))
        return

    def add_file(self, fieldname, filename, fileHandle, mimetype=None):
        """Add a file to be uploaded."""
        body = fileHandle.read()
        if mimetype is None:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        self.files.append((fieldname, filename, mimetype, body))
        return
    
    def __str__(self):
        """Return a string representing the form data, including attached files."""
        # Build a list of lists, each containing "lines" of the
        # request.  Each part is separated by a boundary string.
        # Once the list is built, return a string where each
        # line is separated by '\r\n'.  
        parts = []
        part_boundary = '--' + self.boundary
        
        # Add the form fields
        parts.extend(
            [ part_boundary,
              'Content-Disposition: form-data; name="%s"' % name,
              '',
              value,
            ]
            for name, value in self.form_fields
            )
        
        # Add the files to upload
        parts.extend(
            [ part_boundary,
              'Content-Disposition: file; name="%s"; filename="%s"' % \
                 (field_name, filename),
              'Content-Type: %s' % content_type,
              '',
              body,
            ]
            for field_name, filename, content_type, body in self.files
            )
        
        # Flatten the list and add closing boundary marker,
        # then return CR+LF separated data
        flattened = list(itertools.chain(*parts))
        flattened.append('--' + self.boundary + '--')
        flattened.append('')
        return '\r\n'.join(flattened)


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

sfname=[]
namelist=[]
listempty=threading.Semaphore(value=1)
listempty.acquire()
		
def uploadsongs():
	global sfname
	global namelist
	global SERVER,ROOT
	while True:
		if len(sfname)!=0:
			listempty.release()
		listempty.acquire()
		if len(sfname)==0:
			continue;
		msg=sfname[0]
		form=MultiPartForm()
		form.add_file('upfile',msg,fileHandle=StringIO(open(msg).read()))
		if(os.path.isfile(msg+'.info.json')):
			form.add_file('filejson',msg,fileHandle=StringIO(open(msg+'.info.json').read()))
		else:
			form.add_file('filejson',msg,fileHandle=StringIO("No Info"))
		request=urllib2.Request('http://'+SERVER)
		body = str(form)
		request.add_header('Content-type', form.get_content_type())
		request.add_header('Content-length', len(body))
		request.add_header('songname', namelist[0])
		request.add_data(body)
		try:
			urllib2.urlopen(request)
		except:
			pass
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
def chkexisting(fname):
	return (os.path.isfile(fname))
def download_youtube(link):
	global sem	
	if(len(link)==0):
		return;
	fname=re.findall("\?v=(.*?)\&",link+"&")[0]
	try:
		if(len(re.findall("http",link))==0):
			link="http://"+link
		nl=re.findall("span id=\"eow-title\".*?title=\"(.*?)\"",urllib.urlopen(link).read())
		if(len(nl)==0): 
			nl=fname
		else:
		 	nl=nl[0]
	except:
		nl=fname
	infname=fname+".info.json"
	ninffile=nl+".info.json"
	if(chkexisting(os.path.join(CACHEFOLDER,fname))==True):
		shutil.move(os.path.join(CACHEFOLDER,fname),os.path.join(CACHEFOLDER,nl))
		shutil.move(os.path.join(CACHEFOLDER,infname),os.path.join(CACHEFOLDER,ninffile))
	if(chkexisting(os.path.join(CACHEFOLDER,nl))==False):
		loc=os.path.join(CACHEFOLDER,"%(id)s")
		fd=youtubedl.FileDownloader({"outtmpl":loc})
		for e in youtubedl.gen_extractors():
			fd.add_info_extractor(e)
		fd.download([link])
		shutil.move(os.path.join(CACHEFOLDER,fname),os.path.join(CACHEFOLDER,nl))
		shutil.move(os.path.join(CACHEFOLDER,infname),os.path.join(CACHEFOLDER,ninffile))
	addsong(os.path.join(CACHEFOLDER,nl),nl)

def download(link,tmp):
	global songlist
	global namelist
	global down
	global sem,CACHEFOLDER
#	print len(link)
	while(down>=5):
		continue
	down+=1
	if len(re.findall("youtube",link))!=0:
		download_youtube(link)
	elif(len(link)>4):
		if(link[-4:]==".mp3"  and len(re.findall(link,"www"))!=0):
			loc=urllib.urlretrieve(link)[0]
			addsong(os.path.join(CACHEFOLDER,os.path.basename(loc)),os.path.basename(loc))
		else:
			link=os.path.join(CACHEFOLDER,link)
			if(os.path.isfile(link)):
				addsong(link,link)
	down-=1
class FormPage(Resource):

	def render_GET(self,request):
		global ROOT
		global curplist
		request.setResponseCode(200)
		if(request.prepath==["download"]):
			if(request.args.get('link')!=None):
				start_new_thread(download,(request.args['link'][0],0))
				return "<meta http-equiv=\"REFRESH\" content=\"0;url=http://localhost:8881\">"
		elif(request.prepath==["getplist"]):
			curplist=(urllib2.urlopen(urllib2.Request(SERVERWITHPORT+"/getplaylist")).read())
			return curplist
		else:
			curplist=(urllib2.urlopen(urllib2.Request(SERVERWITHPORT+"/getplaylist")).read())
			ret=open("clientui.html").read()%curplist
			return ret



def updateplaylist():
	global host
	global sock
def terminput():
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
		thread.start_new_thread(download,(msg,1234))
def getcurpacket():
	global sendsock,recvsock,SERVERLISTENPORT,SERVERIP
	sendsock.sendto("",(SERVERIP,SERVERLISTENPORT))
	data,addr = recvsock.recvfrom(1024)
	return tuple(data.split('::'))
	
def playhere():
	global curplist,CACHEFOLDER
	p=mplayer.Player()
	curname=""
	while(True):
		time.sleep(1)
		songname,curloc,status=getcurpacket()
		try:
			float(curloc)
			if(songname!=curname):
				p.loadfile(os.path.join(CACHEFOLDER,songname))
				curname=songname
			if(status!=str(p.paused)):
				p.pause()
			if(abs(p.time_pos-float(curloc))>0.5):
				p.time_pos=float(curloc)
		except:
			pass
#		if(len(curplist)!=0):
#			os.system("mplayer -really-quiet -udp-slave -udp-ip=localhost -udp-port=24345 \"%s\"",re.findall(curpli)
os.system(PROXYLIST)
recvsock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
recvsock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
recvsock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)	
recvsock.bind(("127.0.0.1",LISTENPORT))
sendsock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
root=Resource()
root.putChild("getplist",FormPage())
root.putChild("download",FormPage())
start_new_thread(playhere,())
root.putChild("",FormPage())
factory=Site(root)
reactor.listenTCP(WEBINTERFACE_PORT,factory)
thread.start_new_thread(uploadsongs,())
start_new_thread(terminput,())
reactor.run()
#s.close()
