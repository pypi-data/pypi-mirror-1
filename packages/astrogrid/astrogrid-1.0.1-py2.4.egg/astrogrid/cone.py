"""
Send a cone search query to a service.

A cone search is a query of a catalogue for objects around a position
in sky.	 This module implements the basic cone search, given a service
provider and the coordinates and radius of the area in sky, returns a
list of objects.

"""
__id__ = '$Id: cone.py 97 2007-05-29 15:51:00Z eddie $'
__docformat__ = 'restructuredtext en'

import os, tempfile, urlparse
import re
from astrogrid import acr
from utils import mkURI
from watcherrors import watcherrors, needslogin

class ConeSearch:
	"""
	The following example sends a cone search query to NED and saves the
	resulting VOTable in the local disk.

	   >>> from astrogrid import ConeSearch
	   >>> cone = ConeSearch("ivo://ned.ipac/Basic_Data_Near_Position")
	   >>> print cone.info['content']['description']
	   >>> result = cone.execute(242.811, 54.596, 0.1)
	   >>> open("ned.vot",'w').write(result)

	:IVariables:
	  info
		Information about the service
	"""
	@watcherrors
	def __init__(self, service, dsatab=None):
		"""
		:Parameters:
		  service : str
			URI of service to be queried
			(e.g. "ivo://ned.ipac/Basic_Data_Near_Position")
		"""

		# Uses the cone within acr.ivoa
		self.cone = acr.ivoa.cone
		self.service = service 
		self.dsatab = dsatab

		# Queries the registry for information on service
		self.info = acr.ivoa.registry.getResource(self.service)
		#if self.info['type'].find('ConeSearch')==-1:
		#	 acr._ELOG("Service %s is not a ConeSearch type" % self.service)
		#	 self.cone=None
		#	 return None
		
		acr._DLOG("Will query %(title)s" % self.info)
		self.description = self.info['content']['description']
		self.title = self.info['title']

	@watcherrors			
	def execute(self,ra, dec, radius, saveAs=None, clobber=False, dsatab=None):
		"""
		Execute the cone search.

		:Parameters:
		   ra : float
			 R.A. in degrees
		   dec : float
			 Dec in degrees
		   radius : float
			 Radius in degrees

		:Keywords:
		   saveAs : str
			 Saves the query to a file in MySpace. 
			 Default: None
		   clobber : bool
			 Overwrites file if it exists (takes priority over configuration file)
		   dsatab : str
			 DSA Table (default is first one)	

		:Return:
		  res : str
			VOTable as a string or the name of the output file if `saveAs`
			was used.

		"""
		# Constructs the correct query from the information on the registry
		query = self.cone.constructQuery(self.service, ra, dec, radius)

		if not dsatab:
			dsatab = self.dsatab

		if dsatab:
			try:
				a = re.compile('\S+&(DSATAB=\S+)&RA\S+').match(query).group(1)
				query = query.replace(a, 'DSATAB=%s' % dsatab)
			except:
				pass
		
		self.query = query

		acr._DLOG('Submitting query %s' % query)

		if saveAs:
			if not acr.isLoggedIn():
				if acr._config.get('autologin', False):
					acr.login()
				else:
					acr._ELOG('Trying to save file in MySpace. Not logged in')
					return None
					
			ofile = mkURI(saveAs)
			if acr.astrogrid.myspace.exists(ofile):
				acr._DLOG('File %s exists' % ofile)
				if clobber==True or acr._config.get('clobber', False):
					acr._WLOG('File Exists. Clobbering')
				else:
					acr._ELOG('File Exists. Not Clobbering')
					return ofile
					
			acr._DLOG("Saving as %s" % ofile)
			self.cone.executeAndSave(self.query,ofile)
			res = ofile
		else:
			res = self.cone.executeVotable(self.query)
				
		return res
