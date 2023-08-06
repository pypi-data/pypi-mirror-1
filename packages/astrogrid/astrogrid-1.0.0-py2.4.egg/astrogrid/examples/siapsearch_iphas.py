
import os
from astrogrid import SiapSearch
from astrogrid.plastic import broadcast
from optparse import OptionParser
import time

siap=SiapSearch('ivo://uk.ac.cam.ast/IPHAS/images/SIAP')
votable, thread = siap.execute(96,2,1, saveDatasets='#iphasimages/')
while thread.isAlive():
	time.sleep(10)


