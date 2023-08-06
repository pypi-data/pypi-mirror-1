"""
Send queries to a stap server.
"""
__id__ = '$Id: stap.py 97 2007-05-29 15:51:00Z eddie $'

__docformat__ = 'restructuredtext en'

import os
from astrogrid import acr
from utils import mkURI
import exceptions
import datetime
from threadmethod import threadmethod
from watcherrors import watcherrors, needslogin

class StapSearch:
    """
    Execute STAP searches.
    
    The following example sends a cone search query to NED and saves the
    resulting VOTable in the local disk.

       >>> from astrogrid import StapSearch
       >>> stap = StapSearch('ivo://mssl.ucl.ac.uk/stap/vso/eit')
       >>> print stap.info['content']['description']       
       >>> result = stap.execute(180.0, 2.0, 1.0)
       >>> open('stap_eit.vot','w').write(result)
       
    The following example saves the images from the query to a directory in MySpace. 
    The execute query returns in this case a Thread instance that can be queried for
    completion.
    
       >>> res, thread = siap.execute(180.0, 2.0, 0.1, saveDatasets='#sdss/images/')
       >>> thread.isAlive()
       True
       >>> thread.isAlive()
       False

    :IVariables:
      info
        Information about the service
    """    
    @watcherrors
    def __init__(self, service):
        """
        :Parameters:
          service : str
            URI of service to be queried
            (e.g. 'ivo://mssl.ucl.ac.uk/stap/vso/eit')

        :Keywords:
          debug : bool
            Print debugging information. Default = False
        """
        # Uses stap within acr.astrogrid
        self.stap = acr.astrogrid.stap
        self.service = service

        # Queries the registry for information on service
        self.info = acr.ivoa.registry.getResource(self.service)
        if self.info['type'].find('SimpleTime')==-1:
            acr._ELOG("Service %s is not a SimpleTimeAccess type" % self.service)
            return None

        acr._DLOG("Will query %(title)s" % self.info)
        self.description = self.info['content']['description']
        self.title = self.info['title']
        
    @watcherrors
    def execute(self, start, end, format='ALL',
                saveAs=None, clobber=False, saveDatasets=None):
        """
        Execute the cone search.

        :Parameters:
           start : datetime
             Start date and time
           end : datetime
             Start date and time

        :Keywords:
           saveAs : str
             Saves the query to a file in MySpace.
             Default: None
           clobber : bool
             Overwrites file if it exists (takes priority over configuration file)
           saveDatasets : str
             If the name of a directory in MySpace is specified saves asynchronously 
             the files of the siap query.

        :Return:
          res : str
            VOTable as a string or the name of the output file is `saveAs`
            was used.
          thread
            If saveDatasets then returns the thread so it can be queried for
            completion.
        """
        
        # Constructs the correct query from the information on the registry
        query = self.stap.constructQueryF(self.service, start, end, format)

        acr._DLOG('Executing query %s' % query)
            
        if saveAs or saveDatasets:
            if not acr.isLoggedIn():
                if acr._config.get('autologin', False):
                    acr.login()
                else:
                    acr._ELOG('Trying to access MySpace. Not logged in')
                    return None

        if saveAs:        
            ofile = mkURI(saveAs)
            if acr.astrogrid.myspace.exists(ofile):
                acr._DLOG('File %s exists' % ofile)
                if clobber==True or acr._config.get('clobber', False):
                    acr._WLOG('File Exists. Clobbering')
                    acr._DLOG("Saving as %s " % ofile)
                    self.stap.executeAndSave(query,ofile)
                    res = ofile
                else:
                    acr._ELOG('File Exists. Not Clobbering')
                    res = None
            else:
                self.stap.executeAndSave(query,ofile)
                res = ofile
        else:
            res = self.stap.executeVotable(query)

        if saveDatasets:
            odir = mkURI(saveDatasets)
            if odir[-1]<>'/': odir+='/'
            acr._DLOG('Saving datasets to %s' % odir)
            t = self._saveDatasets(query, odir)
            if not res: 
               res=t
            else:
               res=(res, t)

        return res

    @threadmethod()
    def _saveDatasets(self, query, odir):        
        self.stap.saveDatasets(query, odir)
