"""
Module to send queries to query the registry.

"""
__id__ = '$Id: system.py 97 2007-05-29 15:51:00Z eddie $'

import UserDict
from astrogrid import acr

class Configuration(UserDict.UserDict):
    def __init__(self):
        d = acr.system.configuration.list()
        self.data={}
        for k in d.keys():
            self[k]=d[k]

    def update(self, dd):
    	for key in dd:
	        acr.system.configuration.setKey(key, dd[key])
        self[key]=dd[key]

        
            

    
