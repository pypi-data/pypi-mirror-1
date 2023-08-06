"""
Python interface to MySpace

"""
__id__ = '$Id: myspace.py 118 2007-06-18 11:22:21Z eddie $'
__docformat__ = 'restructuredtext en'

import os
import tempfile
from astrogrid import acr, Community
import urllib2, urlparse
import urllib
from utils import mkURI
from watcherrors import watcherrors, needslogin

class MySpace:
	"""
	Perform operations in MySpace.
	
	  >>> from astrogrid import MySpace
	  >>> m = MySpace()
	  >>> m.ls()	# list contents
	  >>> m.rm('test8', recursive=True)	 # recursively remove the test8 directory
	  
	Saving data to MySpace:
	
	  >>> m.savefile('image.fits', '#images/image.fits')
	  >>> m.savefile('http://www.example.com/image.fits', '#images/image.fits', clobber=True)
	  >>> m.savefile(open('image.fits').read(), '#images/image.fits')
	 
	"""
	@watcherrors
	def __init__(self):
		self.community = acr.astrogrid.community
		self.myspace = acr.astrogrid.myspace

	@watcherrors
	@needslogin
	def home(self):
		"""Return the home IVORN"""
		return acr.astrogrid.myspace.getHome()

	@watcherrors
	@needslogin
	def ls(self, directory=None, pprint=False, recursive=False, depth=0):
		"""List contents of directory"""
		if not self.community.isLoggedIn():
			print 'Not logged in'
			return None

		if not directory:
			directory = self.home()
			n = directory
		else:
			n = mkURI(directory)
			
		ni = acr.astrogrid.myspace.getNodeInformation(n)
		
		nl = acr.astrogrid.myspace.listIvorns(n)

		res=[]
		for n in nl:
			ni = acr.astrogrid.myspace.getNodeInformation(n)
			res.append([ni['size'], ni['modifyDate'].value, ni['name'], ni['folder']])
			if pprint:
				#print "%s %s %s%s" % (ni['size'], ni['modifyDate'], ni['name'], ni['folder'] and '/' or '')
				print "%s |- %s%s" % (" "*depth*3, ni['name'], ni['folder'] and '/' or '')
				if recursive and ni['folder']: self.ls(n, pprint, recursive, depth+1)

		if not pprint: return res
		
	def access(self, ivorn):
		"""Checks if the ivorn exists.
		
		:Parameters:
		   ivorn : str
			  File ivorn
		"""
		onode = mkURI(ivorn)
		return self.myspace.exists(onode)
		
	@watcherrors
	@needslogin
	def readfile(self, ivorn, ofile=None):
		"""
		Read a file from MySpace and optionally saves the content to local disk.
		
		:Parameters:
		   ivorn : str
			  File name in MySpace. It can be the full ivorn (i.e. 'ivo://ukidss.roe....')
			  or the path from the root (i.e. '#sdss/dr3qso.vot')
			  
		:Keywords:
		   ofile : str
			  Output file in local disk. Useful for large files since they are not stored
			  in memory prior to being saved. There is no checking that the file already exists.
		"""
		onode = mkURI(ivorn)
		if not self.myspace.exists(onode):
			acr._ELOG('File %s does not exists' % onode)
			return None
			
		url = self.myspace.getReadContentURL(onode)
		if ofile:
			urllib.urlretrieve(url, filename=ofile)
			return ofile
			
		return urllib2.urlopen(url).read()
		  
	def rename(self, oldivorn, newivorn):
		"""Rename a MySpace resource"""
		o = mkURI(oldivorn)
		n = mkURI(newivorn)
		if self.myspace.exists(n):
			acr._ELOG('File Exists. Not Clobbering')
			return False
		
		self.myspace.rename(o, n)
		return True
		
	@watcherrors
	@needslogin
	def savefile(self, data, ivorn, clobber=False):
		"""
		Saves data into MySpace. 
		
		:Parameters:
		   data
			  Data string to copy. It can be a http or ftp reference, a local file or the
			  data itself.
		   ivorn : str
			  File name in MySpace. It can be the full ivorn (i.e. 'ivo://ukidss.roe....')
			  or the path from the root (i.e. '#sdss/dr3qso.vot')
			  
		:Keywords:
			clobber : bool
			   Clobber exiting file. Default: False
			   
		:Returns:
			result : bool
			   True if operation succeeded.
		
		"""
		onode = mkURI(ivorn)
		if self.myspace.exists(onode):
			acr._DLOG('File %s exists' % onode)
			if clobber==True or acr._config.get('clobber', False):
				acr._WLOG('File Exists. Clobbering')
			else:
				acr._ELOG('File Exists. Not Clobbering')
				return None
		else:
			self.myspace.createFile(onode)
			
		if data[:4]=='http' or data[:3]=='ftp':
			tmpURL = data
		elif os.path.isfile(data):
			tmpURL = urlparse.urlunsplit(['file','',os.path.abspath(data),'',''])
		else:
			tmpFile = tempfile.mktemp(".vot")
			open(tmpFile,'w').write(data)
			tmpURL = urlparse.urlunsplit(['file','',os.path.abspath(tmpFile),'',''])
			
		res = self.myspace.copyURLToContent(tmpURL, onode)
		return res == 'OK'
		
	@watcherrors
	@needslogin
	def mkdir(self, ivorn):
		"""Create a directory."""
		node = mkURI(ivorn)
		if not self.myspace.exists(node):
			 return self.myspace.createFolder(node) == 'OK'
		else:
			acr._WLOG('Directory already exists.')
		return False
		
	@watcherrors
	@needslogin
	def rm(self, ivorn, recursive=False):
		"""
		Remove a file or directory from MySpace.
		
		:Parameters:
		   ivorn : str
			  File or directory in MySpace. It can be the full ivorn (i.e. 'ivo://ukidss.roe....')
			  or the path from the root (i.e. '#sdss/dr3qso.vot')
			  
		:Keywords:
			recursive : bool
			   If True then directories are removed recursively.
		"""
		node = ivorn
		node = mkURI(node)
		if not self.myspace.exists(node):
			acr._ELOG('Node %s not found' % node)
			return None
		nodeinfo = self.myspace.getNodeInformation(node)
		if nodeinfo['file']:
			acr._DLOG('Deleting %s' % nodeinfo['name'])
		elif nodeinfo['folder']:
			contents = self.myspace.listIvorns(node)
			if recursive:
				acr._DLOG("Drilling down into %s" % nodeinfo['name'])
				for f in self.myspace.listIvorns(node):
					self.rm(f, True)
			try:
				acr._DLOG('Deleting folder %s' % nodeinfo['name'])
			except:
				acr._DWARN('Folder %s is not empty' % nodeinfo['name'])
		else:
			acr._WLOG('Node %s not recognised' % nodeinfo['name'])
			
		try:
			self.myspace.delete(node)
		except Exception, e:
			acr._WLOG(str(e))
			
		
	@watcherrors
	@needslogin
	def convertfile(self, ifile, ofile, ifmt='votable', ofmt='fits', clobber=False):
		"""
		Convert one file in MySpace to another format (e.g. useful to convert from
		votable to fits and then download the fits). To convert a file already in
		the local disk use utils.convertfile
		
		:Parameters:
		   ifile : str
			  Input file
		   ofile : str
			  Output file
		
		:Keywords:
		   ifmt : str
			  Input file format (votable|fits|csv). Default: votable
		   ofmt : str
			  Output file format (votable|fits|csv). Default: fits
		   clobber : bool
			  Clobber existing file. Default: False
			  
		:Returns:
			result : bool
			   True if operation succeeded.
		"""
		inode = mkURI(ifile)
		onode = mkURI(ofile)
		if self.myspace.exists(onode):
			acr._DLOG('File %s exists' % onode)
			if clobber==True or acr._config.get('clobber', False):
				acr._WLOG('File Exists. Clobbering')
			else:
				acr._ELOG('File Exists. Not Clobbering')
				return None
		else:
			self.myspace.createFile(onode)
		 
		acr._DLOG('Converting %s (%s) to %s (%s)' % (inode, ifmt, onode, ofmt))
		res = acr.util.tables.convertFiles(inode, ifmt, onode, ofmt)
		return res == 'OK'
