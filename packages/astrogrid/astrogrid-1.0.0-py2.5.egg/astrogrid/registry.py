"""
Module to send queries to query the registry.

"""
__id__ = '$Id: registry.py 97 2007-05-29 15:51:00Z eddie $'

from astrogrid import acr
from watcherrors import watcherrors, needslogin

class Registry:
    """Perform queries on the registry"""
    
    @watcherrors
    def __init__(self):
        self.registry = acr.ivoa.registry
        # self.identity = self.registry.getIdentity()

    def __getitem__(self, id):
        try:
            res=self.registry.getResource(id)
        except:
            res=self.search(id)
        return res

    @watcherrors
    def endpoint(self):
        """Returns the IVORN of the registry endpoint"""
        return self.registry.getSystemRegistryEndpoint()
    
    @watcherrors
    def keywordSearch(self, keywords, orValues=False):
        """Performs a keyword search on the registry"""
        return self.registry.keywordSearch(keywords, orValues)


    search = keywordSearch
        
    @watcherrors
    def searchCone(self, key=None):
        """Return all services which provide a cone interface"""
        xq=acr.ivoa.cone.getRegistryXQuery()
        return self._xquery(xq, key=key)
    
    @watcherrors
    def searchSiap(self, key=None):
        """Return all services which provide a siap interface"""
        xq=acr.ivoa.siap.getRegistryXQuery()
        return self._xquery(xq, key=key)
    
    @watcherrors
    def searchStap(self, key=None):
        """Return all services which provide a stap interface"""
        xq=acr.astrogrid.stap.getRegistryXQuery()
        return self._xquery(xq, key=key)
        
    def _xquery(self, xq, key=None, searchDescription=True):
        tres = self.registry.xquerySearch(xq)
        # Search within results until I know how to do this properly using XQuery
        res=[]
        if key:
            for r in tres:
                for k in ['title', 'id', 'shortName']:
                    if r.has_key(k):
                        if r[k].find(key)<>-1: res.append(r)
                if r.has_key('contents') and searchDescription:
                    if r['contents'].has_key('description'):
                        if r['contents']['description'].lower().find(key.lower())<>-1: res.append(r)
        else:
            res = tres
            
        return res

        
