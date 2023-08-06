#!/usr/bin/python
"""

python script.py /home/allen/Desktop/fathi/Sample/brightest.csv

"""

# Import modules
import os, sys
import re
import commands
import urllib
import logging
from astrogrid import SiapSearch

# Configure logging
logging.basicConfig(level=logging.INFO, filename='script.log', filemode='w')

# Read input table (CSV)
import csv
reader=csv.reader(open(sys.argv[1], "rb"))
ra=[]
dec=[]
reader.next()
for row in reader:
   ra.append(float(row[0]))
   dec.append(float(row[1]))

# Initialize siap service search and name resolver
# siap = SiapSearch('ivo://nasa.heasarc/skyview/sdss')
siap = SiapSearch('ivo://sdss.jhu/services/SIAPDR5-images')

# Loop for each object
for i in range(len(ra)):
  # Execute SIAP search 2 arcsec box size
  out = siap.execute(ra[i], dec[i], 2.0/3600.0)
  # Output dir is sdss + number of object in the list.
  # Need to change to objID
  output_dir = 'sdss_%d' % i
  # Create directory if it does not exist
  if not os.access(output_dir, os.R_OK): os.mkdir(output_dir)
  # Write votable containing reference to images
  open(output_dir + '/sdss.vot', 'w').write(out)
  logging.info('File saved: %s' % output_dir + '/sdss.vot')
  # Extract references to images from votable
  images = re.findall('http://\S+fit.gz', out)
  # Loop for each image
  for img in images:
      dr6url = img.replace('DR5','DR6')
      dr6file = output_dir+'/'+img.split('/')[-1]
      # Only do this if coutout not created previously
      if not os.access('%s_cutout.fit' % dr6file[:-7], os.F_OK):
          # Retrieve full image
          urllib.urlretrieve(dr6url, dr6file)
          logging.info('Image retrieved: %s' % dr6url)
          # Gunzip image
          commands.getoutput('gunzip %s' % dr6file)
          # Work out the pixel coords of the object
          res = commands.getoutput('sky2xy %s %f %f' % (dr6file[:-3], ra[i], dec[i]))
          x,y = map(float, res.split()[-2:])
          x,y = round(x), round(y)
          # Create cutout
          x1, x2, y1, y2 = x-75, x+75, y-75, y+75
          if x1<1: x1=1
          if y1<1: y1=1
          if x2>1489: x2=1489
          if y2>1489: y2=1489
          command='imcopy %s[%d:%d,%d:%d] %s_cutout.fit' % (dr6file[:-3], x1, x2, y2, y2,dr6file[:-7])
          logging.info('Cutout created: %s_cutout.fit ' % dr6file[:-7]
          # Remove image
          os.unlink(dr6file)