#!/usr/bin/python
"""This example shows how to submit a list of ra,dec positions to SDSS DR5.
"""

import sys, time
from numpy import *
import math

from astrogrid import ConeSearch
from astrogrid.threadpool import easy_pool

# Define the service endpoint IVORN
cone=ConeSearch('ivo://wfau.roe.ac.uk/sdssdr5-dsa/dsa', dsatab='PhotoObjAll')

# Generate 20 random positions.
# In real astronomy these would be read from a file
nsrc=20
ra=random.rand(nsrc)*2*pi*math.degrees(1)
dec=(random.rand(nsrc)*pi-pi/2.)*math.degrees(1)
radius=ones(nsrc)*0.001

for i in range(nsrc):
	res = cone.execute(float(ra[i]), float(dec[i]), float(radius[i]))
	open('sdss%02d.vot' % (i+1), 'w').write(res)
	print i+1, 'sdss%02d.vot' % (i+1)
