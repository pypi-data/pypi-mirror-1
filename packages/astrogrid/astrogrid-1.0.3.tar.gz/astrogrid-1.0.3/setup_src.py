__id__='$Id: setup.py 97 2007-05-29 15:51:00Z eddie $'

from distutils.core import setup
import os
import sys
import string

execfile(os.path.join("astrogrid", "release.py"))

python_version = sys.version.split()[0].split(".")
if map(int, python_version[:2]) < [2, 4]:
	print "You need at least Python version 2.4"
	sys.exit()
    
print 'Python version %s detected. Installing.\n' % ('.'.join(version))

setup(name = "astrogrid",
      version = version,
      description = "Python Interface to ACR",
      author = author,
      author_email = email,
      maintainer_email = email,
      license = "http://www.astrogrid.org/LICENSE",
      long_description="",
      url = "http://www.astrogrid.org",
      platforms = ["Linux","Solaris","Mac OS X","Win"],
      packages = ['astrogrid'],
      package_dir = {'astrogrid': 'astrogrid'},
      package_data = {'astrogrid': ['*.chm']}
      )

sys.exit()

