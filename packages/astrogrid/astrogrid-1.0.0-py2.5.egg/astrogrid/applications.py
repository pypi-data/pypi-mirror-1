"""
Run server side applications.
"""
__id__ = '$Id: applications.py 113 2007-06-08 13:52:15Z eddie $'
__docformat__ = 'restructuredtext en'

from astrogrid import acr
import utils
from watcherrors import watcherrors, needslogin

class Applications:
	"""
	This is the main class to send applications to be run remotely and asynchronously in the system.
	
	Example:
	
	   >>> from astrogrid import Applications
	   >>> app = Applications('ivo://starlink.ac.uk/stilts1.3', 'tcopy')
	   ... fill in app.inputs and app.outputs ...
	   >>> run1 = app.submit()
	   ... fill in app.inputs and app.outputs with other values ...
	   >>> run2 = app.submit()
	   >>> run1.status()
	   COMPLETED
	   >>> run2.status()
	   RUNNING
	   
	"""
	@watcherrors
	def __init__(self, ivorn=None, interface='default'):
		"""
		:Parameters:
		  ivorn : str
			String containing the IVORN of the job to be submitted

		:Keywords:
		  interface : str
			If the application provides various interfaces, the specify the
			chosen one here, otherwise it will pick up the default.

		"""
		self.applications = acr.astrogrid.applications
		#self.applist = acr.astrogrid.applications.list()
		#if (ivorn is not None) and (ivorn not in self.applist):
		#	 print 'ERROR: application not found'
		#elif ivorn:
		try:
			acr._DLOG('Trying template for IVORN %s (%s)' % (ivorn, interface))
			self.template(ivorn, interface)
		except:
			acr._WLOG('Interface %s not found. Using default' % interface)
			self.template(ivorn, 'default')
			
		self.servers = acr.astrogrid.applications.listServersProviding(ivorn)

	@watcherrors
	def list(self):
		"""Return a list of all applications"""
		return self.applist

	#@watcherrors
	def template(self, ivorn, interface='default'):
		self.ivorn = ivorn
		self.interface = interface
		self.__struct = self.applications.createTemplateStruct(ivorn, interface)
		#try:
		#	self.info = self.applications.getCeaApplication(ivorn)
		#	self.doc = self.applications.getDocumentation(ivorn)
		#except:
		#	acr._WLOG('Failed to retrieve information for task.')
		self.inputs = self.__struct['input']
		self.outputs = self.__struct['output']


	@watcherrors
	@needslogin
	def submit(self, server=None, validate = True):
		"""
		Submits a job.

		:Keywords:
		  server : str
			Server to send the job to. If not defined just picks one.
		  validate : bool
			Validate document before submitting. Default: True
			
		:Return:
		   ceapp
			 An instance of CEApp allowing to check status and get results.

		"""
		acr.login()
				
		self._checkParams()
		
		doc = self.applications.convertStructToDocument(self.__struct)
		if validate: self.applications.validate(doc)
		if not server:
			execId = self.applications.submit(doc)
		else:
			execId = self.applications.submitTo(doc, server)

		return CEApp(execId)

	def _checkParams(self):
		for f in self.inputs:
			v = self.inputs[f].get('value', '')
			if str(v)[:1]=='#':
				self.inputs[f]['value']=utils.mkURI(v)
				self.inputs[f]['indirect']=True
			if str(v)[:5] in ['ivo:/', 'http:', 'ftp:/']:
				self.inputs[f]['indirect']=True
				
		for f in self.outputs:
			v = self.outputs[f].get('value','')
			if str(v)[:1]=='#':
				self.outputs[f]['value']=utils.mkURI(v)		 
				self.outputs[f]['indirect']=True
			if str(v)[:5] in ['ivo:/', 'http:', 'ftp:/']:
				self.outputs[f]['indirect']=True

	def _getToolDoc(self):
		return self.applications.convertStructToDocument(self.__struct)
		
	
class DSA:
	"""
	
	   >>> from astrogrid import DSA
	   >>> mydsa = DSA('ivo://wfau.roe.ac.uk/twomass-dsa/ceaApplication')
	   >>> mydsa.query(adqlx)
	
	:IVariables:
	   info
		  Details of the application
	   doc
		  Documentation about the application
	"""
	def __init__(self, service):
		"""
		:Parameters:
		   service : str
			  IVORN of the service to be queried
		
		"""
		self.service = service
		self.app = Applications(service, 'ADQL')
		if not self.app:
			return None
		try:
			self.info = self.app.info
			self.doc = self.app.doc
		except:
			pass

		self.formats={'votable': 'VOTABLE', 
					  'votbin': 'VOTABLE-BINARY', 
					  'csv': 'COMMA-SEPARATED'}
		
	def query(self, sql, ofmt='votable', saveAs=None):
		"""
		:Parameters:
		   sql : str
			 SQL query
			 
		:Keywords:
		  ofmt : str
			 Output format (votable|votbin|csv). Default: vot
		  saveAs : str
			 File name to save the query to in MySpace. Default: None
			 
		:Return:
		   ceapp
			 An instance of CEApp allowing to check status and get results.
		"""
		
		self.app.inputs['Query']['value']=sql
		self.app.inputs['Format']['value']=self.formats[ofmt]
		if saveAs:
			if not acr.isLoggedIn():
				if acr._config.get('autologin', False):
					acr.login()
				else:
					acr._ELOG('Trying to save file in MySpace. Not logged in')
					return None
					
			self.app.outputs['Result']['indirect']=True
			self.app.outputs['Result']['value']=utils.mkURI(saveAs)
			
		return self.app.submit()

		
class CEApp:
	"""Check the status of a CEA running application and return results. An instance of this class is returned by the Applications and DSA classes when submitting a job.
	"""
	def __init__(self, execID):
		self.execID = execID
		self.applications = acr.astrogrid.applications
		
	def status(self):
	
		try:
			acr.ui.lookout.refresh()
		except:
			pass
			
		return self.applications.getExecutionInformation(self.execID)['status']
		
	def info(self):
		return self.applications.getExecutionInformation(self.execID)
		
	def results(self):
		res = self.applications.getResults(self.execID)
		return [res[k] for k in res.keys()]

		
