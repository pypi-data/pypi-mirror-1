#!/usr/bin/python
"""
Given the coordinates of an objects in the command line and a search
radius -- all in degrees -- search the IPHAS catalogue for objects
within the search radius from the given position.

Example:

   conesearch_iphas.py -o iphas.vot 15.45 60.0 0.1
"""
__id__='$Id: conesearch_iphas.py 62 2007-05-10 13:04:34Z eddie $'

import os
from astrogrid import ConeSearch, acr
from optparse import OptionParser
import time

buffer=[l.strip().split(',') for l in open('iphas.test').readlines()]

# We add here the IVORN of the IPHAS service
ivorn = 'ivo://uk.ac.cam.ast/iphas-dsa-catalog/IDR'
cone = ConeSearch(ivorn)
fptr = open('iphas_xmm.list','w')

for obj in buffer[:500]:
	t1=time.time()
	ra,dec=float(obj[0]), float(obj[1])
	radius=10./3600.0
	print 'Querying %s %s %s' % (ra, dec, radius)
	res = cone.execute(ra, dec, radius, dsatab='PhotoObjBest')
	res = acr.util.tables.convert(res, 'votable', 'csv')
	for f in res.split()[1:]:
		fptr.write(f + '\n')
		fptr.flush()
		
	print time.time()-t1
	


