#!/usr/bin/python
"""
Given a list of RA and Dec positions perform a SIAP search saving the 
resultant VOTables and images to MySpace.
"""

import os, re, urllib
from time import sleep
from astrogrid import acr
from astrogrid import SiapSearch

# List of ra and dec. These can be read from a file.
ra = [180.0, 181.0]
dec = [0.0, 0.1]

# Initialize siap service search and name resolver
siap = SiapSearch('ivo://nasa.heasarc/skyview/sdss')

# Create output directory if it does not exist
if not os.access('sdss', os.R_OK): os.mkdir('sdss')

# Loop for each object of the list
for i in range(len(ra)):
	odir = 'sdss/obj%02d' % (i+1)
	if not os.access(odir, os.R_OK): os.mkdir(odir)
	res = siap.execute(ra[i], dec[i], 30.0/3600.0)
	# Save output votable
	open(os.path.join(odir, 'sdss.vot'),'w').write(res)
	# Save the images -- Note the re.compile argument is specific to each service since it
	# depends on how the format the url call to obtain the image. We are only getting here
	# the fits files. It is also possible to obtain the jpegs in the same way.
	j=0
	for img in re.compile('http://.\S+FITS').findall(res):
		print img
		j=j+1
		urllib.urlretrieve(img, os.path.join(odir,'image%d.fits' % j))
		
		
		
