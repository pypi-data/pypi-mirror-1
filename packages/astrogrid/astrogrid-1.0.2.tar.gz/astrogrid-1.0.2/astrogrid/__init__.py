#!/usr/bin/python
"""
This is a functional python interface to the Astrogrid Client Runtime (ACR).

The following classes are provided by

  >>> from astrogrid import *

 * Applications		- run remote applications
 * Community		- account login and logout
 * ConeSearch		- execute a cone search
 * Configuration	- configure AR access
 * DSA				- run a remote ADQL query
 * MySpace			- access to MySpace (i.e. list file, delete, etc.)
 * Registry			- registry search
 * SiapSearch		- execute a siap search
 * StapSearch		- execute a stap search
   
The following additional methods are available from within the acr class

  >>> from astrogrid import acr
  
  * acr.login	   - login 
  * acr.isLoggedIn - returns True/False depending on the user login status
  
In order to use of the class methods, use:

  >>> c = Community()
  >>> c.guiLogin()

See the additional information for each class for the methods that it contains.

Additionally all the ACR calls are available using the acr variable, e.g.,

   >>> from astrogrid import acr
   >>> acr.astrogrid.community.login('user','password','community')


Credits:

	Eduardo A. Gonzalez-Solares
	2008 Astrogrid

"""
__docformat__ = 'restructuredtext en'
__version__ = '1.0.1'
__revision__ = '$Rev: 93 $'
__date__ = '$LastChangedDate: 2007-05-29 15:12:14 +0100 (Tue, 29 May 2007) $'
__id__ = '$Id: __init__.py 183 2007-08-21 09:26:10Z eddie $'

import getpass
import signal
import os, sys, time
import xmlrpclib
import socket
from threadmethod import threadmethod
from SimpleXMLRPCServer import SimpleXMLRPCServer
import urllib2
import urlparse
import tempfile
import logging
import exceptions
from config import _config

_pwd = os.path.dirname(__file__)
	
# Default timeout the for XML-RPC connection
# socket.setdefaulttimeout(30)	

if _config['debug']:
	logging.basicConfig(level=logging.DEBUG)
elif _config['verbose']:
	logging.basicConfig(level=logging.WARN)

try:
	socket.setdefaulttimeout(int(_config['timeout']))
except:
	pass

class SafePlastic:
	def __init_(self):
		pass
		
	def broadcast(self, *args, **kwargs):
		pass
		
	def shutdown(self, *args, **kwargs):
		pass

class PlasticServer:
	"""
	Very simple XML-RPC server. This is how it works:

	server = PlasticServer()
	server.start()
	# ... now it is available from Astroscope, TOPCAT, etc ...
	# Data sent from applications is collected in self.data
	# this needs to be a file in the future.
	# To end the server:
	server.shutdown()
	"""
	def __init__(self, acr):
		self._acr = acr
		self.server = SimpleXMLRPCServer(('localhost', 0))
		self.server.register_instance(self)
		self.finished= False
		self.data = []

	def add_method(self, method, name=None):
		if name is None: name = method.func_name
		class new(self.__class__): pass
		setattr(new, name, method)
		self.__class__ = new
  
	@threadmethod()
	def start(self):
		ipaddr, port = self.server.socket.getsockname()
		msg = ['ivo://votech.org/info/getName',
			   'ivo://votech.org/votable/loadFromURL',
			   'ivo://votech.org/info/getIconURL',
			   'ivo://votech.org/votable/load',
		#		'ivo://votech.org/votable/highlightObject',
		#		'ivo://votech.org/fits/image/loadFromURL',
			   ]

		self.hub = self._acr.plastic.hub
		self.id = self.hub.registerXMLRPC('Python', msg,
										  'http://%s:%s' % (ipaddr, port))

		try:
			acr.system.ui.setStatusMessage('Welcome to Python!')
		except:
			pass
		while not self.finished: self.server.handle_request()
		
	def shutdown(self):
		self.finished = True
		self.hub.unregister(self.id)
		return 0

	def listPlasticApps(self):
		d={}
		for id in self.hub.getRegisteredIds():
			name = self.hub.getName(id)
			d[name.upper()] = id
		return d
		
	def getId(self, app):
		d=self.listPlasticApps()
		return d.get(app.upper(), None)
	
	def broadcast(self, vot, app=None):
		"""
		Sends a votable to listening PLASTIC applications
		
		:Parameters:
		   vot
			  table to broadcast. It can be a string containing the votable or a file.
			  
		:Keywords:	
		   app
			  application to send to (e.g. topcat). Default sends to all listening applications.
			  
		:Return:
		  Returns True if succeeded, False otherwise.
		  
		"""
	
		if vot[:6]=='<?xml ': # Table comes in string format
			vot = acr.util.tables.convert(vot, 'votable', 'votable')
			tmpFile = tempfile.mktemp(".vot")
			open(tmpFile,'w').write(vot)
			tmpURL = urlparse.urlunsplit(['file','',os.path.abspath(tmpFile),'',''])
		elif vot[0]=='#':
			acr.login()
			node = acr.astrogrid.myspace.getHome() + vot[1:]
			tmpURL = acr.astrogrid.myspace.getReadContentURL(node)
		elif vot[:6]=='ivo://': # Table is reference to file in MySpace
			acr.login()
			tmpURL = acr.astrogrid.myspace.getReadContentURL(vot)
		elif os.access(vot, os.F_OK):
			tmpURL = urlparse.urlunsplit(['file','',os.path.abspath(vot),'',''])
		else:
			logging.error('Input format not recognized')
			return
			
		if app:
			recId = self.getId(app)
			self.hub.requestToSubsetAsynch(self.id,'ivo://votech.org/votable/loadFromURL',
										   [tmpURL,tmpURL],[recId])
		else:
			self.hub.requestAsynch(self.id,'ivo://votech.org/votable/loadFromURL',
								   [tmpURL,tmpURL])
		return True


	def loadFromURL(self, sender, message, url):
		if type(url) == type([]):
			url=url[0]

		logging.debug('Plastic message received. Look in acr.plastic.data')
		
		self.data.append([acr.plastic.hub.getName(sender),
						  url, urllib2.urlopen(url).read()])
						  
		return True

	def perform(self, sender, message, url):
		#print sender
		#print message
		#print url
		
		if message == 'ivo://votech.org/info/getIconURL':
			return "http://www2.astrogrid.org/science/documentation/workbench-advanced/advanced-usage/scripting-user-s-guide/python-logo.gif"
		elif message == 'ivo://votech.org/votable/loadFromURL' or mesage == 'ivo://votech.org/votable/load':
			return self.loadFromURL(sender, message, url)
		elif message == 'ivo://votech.org/fits/image/loadFromURL':
			return self.loadFromURL(sender, message, url)
		else:
			print sender, message, url
		


class ACR:
	"""Connect to the Astrogrid ACR. Provides direct access to the XMLRPC methods as well 
	as providing some convenience shortcuts.
	
	Examples:
	
	   >>> from astrogrid import acr
	   >>> acr.login()
	   >>> print acr.system.apihelp.listMethods()
	   >>> print acr.methods
	
	"""
	def __init__(self):
		"""Connects to the Astrogrid ACR"""
		self._connected = False
		self._config = _config
		self.__pid = None
		self._version = __version__
		
#	def starthub(self, sleep=None):
#		"""Start the ACR. Experimental."""
#		if sleep: time.sleep(sleep)
#		
#		if self._connected:
#			self._WLOG('ACR already running.')
#			return
#			
#		javapath = self._config.get('javapath', None)
#		acrpath = self._config.get('acrpath', None)
#		if javapath==None or acrpath==None:
#			self._ELOG('Java or ACR paths not configured.')
#			return
#		if not os.access(javapath, os.F_OK):
#			self._ELOG('Java not found in %s' % javapath)
#			return
#		if not os.access(acrpath, os.F_OK):
#			self._ELOG('ACR not found in %s' % acrpath)
#			return
#			
#		self._DLOG('Starting ACR.')
#		pid = os.spawnv(os.P_NOWAIT, javapath, (javapath, '-Djava.awt.headless=true', '-jar', acrpath))
#		self.__pid = pid
#		i=0
#		while not self._connected and i<3:
#			time.sleep(10)
#			i=i+1
#
#		return True
#		
#	def stophub(self):
#		"""End the ACR. Experimental."""
#		if self.__pid: 
#			os.kill(self.__pid, signal.SIGTERM)
#			acr._connected = False
#			
#	def safeconnect(self, nsec=10):
#		j=0
#		while not self._connected and j<nsec: 
#			time.sleep(1)
#			j = j +1
#		
#		if not self._connected:
#			logging.error('Cannot connect with a running AR hub')
#			return False
#			
#		return True
			
	def _acr_connect(self):
		self._DLOG('Trying connection with running AR')
		filename = '.astrogrid-desktop'
		__propsFile = None

		while True:
			for env in ['HOME', 'HOMEDRIVE', 'HOMEPATH', 'USERPROFILE']:
				p = os.getenv(env)
				if p:
					if os.access(os.path.join(p, filename), os.R_OK):
						__propsFile = os.path.join(p, filename)
						break
			if __propsFile: break
			self._ILOG('Waiting for file ~/.astrogrid-desktop')
			time.sleep(10)
	
		__url = file(__propsFile).readline().rstrip()			
		self.acr = xmlrpclib.Server(__url+"xmlrpc") 
		self.methods = self.acr.system.apihelp.listMethods()
		self.topmethods = list(set([a.split('.')[0] for a in self.methods])) 

		# Now start our Plastic connection
		if self._config['plastic']:
			self.plastic = PlasticServer(self.acr)
			self.plastic.start()
		else:
			self.plastic = SafePlastic()

		self._connected = True
		self.__acr = xmlrpclib.Server(__url+"xmlrpc")		
	
	def startplastic(self):
		if not self._connected: self._acr_connect()
		self.plastic = PlasticServer(self.acr)
		self.plastic.start()
		
	def _DLOG(self, text):
		logging.debug(text)

	def _WLOG(self, text):
		logging.warn(text)

	def _ELOG(self, text):
		logging.error(text)
		
	def _ILOG(self, text):
		logging.info(text)
	
	def autologin(self):
		if not self._connected: self._acr_connect()
		if self.isLoggedIn(): return True
		if self._config['autologin']:
			self.login()
			return True
		else:
			return False
			# username, password, community = self.askpass()
			# self.login(username, password, community)
			
	def askpass(self):
		if not self._connected: self._acr_connect()
		key = None
		if not key and self._config['community'].has_key('default'):
			key = self._config['community']['default']
		if key:
			config = self._config['community'][key]
		else:
			config = self._config['community']
			
		print 'Asking for AstroGrid password.'
		text = 'Username'
		default = config.get('username', '')
		if default: text += ' (%s)' % default
		username = raw_input(' - %s: ' % text)
		if username == '': username = default
		
		text = 'Password'
		default = config.get('password', '')
		password = getpass.getpass(' - %s: ' % text)
		if password == '': password = default
		
		text = 'Community'
		default = config.get('community', '')
		if default: text += ' (%s)' % default
		community = raw_input(' - %s: ' % text)
		if community == '': community = default
		
		return username, password, community
		
	def login(self, username=None, password=None, community=None):
		"""Convenience method to login.
		
		:Keywords:
		   username : str
			  User name
		   password : str
			  Password
		   community : str
			  Community
		
		"""
		if not self._connected: self._acr_connect()
		key = None
		if username and (not password and not community): 
			key = username
			username =None
		
		if not key and self._config['community'].has_key('default'):
			key = self._config['community']['default']
			
		if key:
			config = self._config['community'][key]
		else:
			config = self._config['community']
			
		if not username: username = config.get('username', None)
		if not password: password = config.get('password', None)
		if not community: community = config.get('community', None)
		
		if username==None or password==None or community==None:
			username, password, community = self.askpass()
			
		c = Community()
		if c:
			return c.login(username, password, community)
		
	def isLoggedIn(self):
		if not self._connected: self._acr_connect()
		"""Convenience method to check if logged in"""
		c = Community()
		if c:
			return c.isLoggedIn()

	def logout(self):
		if not self._connected: self._acr_connect()
		c = Community()
		if c: return c.logout()
		
	def __getattr__(self, attr):
		logging.debug('getattr:%s' % attr)
		if not self._connected: self._acr_connect()
		if attr in ['login()']:
			return
		if attr[:7] == '_config':
			return
			
		try:
			if attr in self.topmethods:
				return getattr(self.acr, attr)
			else:
				return None
		except:
			return None
		
	def require(self, version):
		if version<self._version:
			 raise exceptions.Exception, 'Required AR version not found'
		
#	def __del__(self):
#		self.plastic.shutdown()
		
acr = ACR()

# Import additional modules

from cone import ConeSearch
from siap import SiapSearch
from stap import StapSearch
from registry import Registry
from system import Configuration
from community import Community
from myspace import MySpace
from sesame import sesame
from applications import Applications, DSA
from helpbrowser import aghelp

