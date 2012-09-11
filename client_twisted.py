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
from cStringIO import StringIO
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor
from thread import *


	

COMMANDS=['extra']

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
	global SERVER
	while True:
		if len(sfname)!=0:
			listempty.release()
		listempty.acquire()
		msg=sfname[0]
		proxy_handler = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(proxy_handler)
		urllib2.install_opener(opener)
		
		form=MultiPartForm()
		form.add_file('upfile',msg,fileHandle=StringIO("abcd1234"))
		request=urllib2.Request('http://'+SERVER)
		print "http://" + SERVER
		body = str(form)
		request.add_header('Content-type', form.get_content_type())
		request.add_header('Content-length', len(body))
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
	print os.path.join(os.getcwd(),fname)
	if(chkexisting(fname)==False):
		if not os.path.isfile(os.getcwd()+"/"+fname+".mp4") :
			fd=youtubedl.FileDownloader({"outtmpl":u'%(id)s'})
			for e in youtubedl.gen_extractors():
				fd.add_info_extractor(e)
			fd.download([link])
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
	addsong(os.path.join(os.getcwd(),fname),nl)

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
class FormPage(Resource):
	def render_GET(self,request):
		if(request.args.get('link')!=None):
			print request.args['link']
			start_new_thread(download,(request.args['link'][0],0))


def updateplaylist():
	global host
	global sock


root=Resource()
root.putChild("download",FormPage())
SERVER=sys.argv[1]
factory=Site(root)
reactor.listenTCP(8881,factory)
thread.start_new_thread(uploadsongs,())
reactor.run()

#while True:
#	msg=raw_input("Client >> ")
#	msg=msg.rstrip()
#	msg=msg.lstrip()
#	if len(msg)>8:
#		if(msg[0]=='\''):
#			msg=msg[1:]
#		if(msg[-1]=='\''):
#			msg=msg[:-1]
#	print msg
#	thread.start_new_thread(download,(msg,1234))
#s.close()
