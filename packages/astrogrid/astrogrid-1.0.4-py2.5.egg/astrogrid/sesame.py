"""
Queries Vizier, Simbad and NED in order to resolve a name into coordinates.
"""

__docformat__ = 'restructuredtext en'

import VOTable, urllib2, urllib
import sys
from StringIO import StringIO

web = 'http://cdsweb.u-strasbg.fr/viz-bin/nph-sesame/-oxpi/SNVA?'

class sesame:
    """
    Uses Simbad, Ned and Vizer to resolver name into coordinates

    Example:

       >>> s = sesame()
       >>> pos, a, d = s('M31')
       

    """
    
    def __init__ (self):
        self.web = web

    def resolve (self, name):
        """
        Return the position given an object name (J2000)

        Inputs:
           name    - Name of the object

        Outputs:
           pos     - String representation of coordinates
           a, d    - Coordinates in decimal degrees

        """
        i=0
        result=[]
        while i<10:
            try:
                res = urllib2.urlopen(self.web + urllib.urlencode([('obj', name)]).split('=')[1]).read()
                self.xml = VOTable.VOXML (StringIO (res))
                result = self.xml.root.Sesame.Target.Resolver
                break
            except:
                pass
                
            i+=1

        pos=''
        for r in result:
            try:
                pos = r.jpos.content
                break
            except AttributeError:
                pass

        a,d=pos.split()
        a = map(float, a.split(':'))
        d = map(float, d.split(':'))
        a = 15.0*(a[0]+a[1]/60.0+a[2]/3600.0)
        d = (d[0]+d[1]/60.0+d[2]/3600.0)

        return pos, a, d
