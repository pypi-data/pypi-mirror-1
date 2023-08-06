# The encryption stuff has been copied from: http://www.daniweb.com/code/snippet391.html
import sys, os, stat, md5
from astrogrid.configobj import ConfigObj
import getpass
import StringIO
import operator
import urllib

python_acr="""
# This is a skeleton configuration file for ACR access from Python
# Add your credentials to the different communities and copy it to
# $HOME/.python-acr (UNIX) or $HOME/_python-acr (Windows) and make sure 
# that it is only readable for the owner: chmod 0600 $HOME/.python-acr

debug = False
verbose = True
autologin = True
plastic = False
timeout = None

[community]
# We choose Leicester as the default community
default = leicester

[[ukidss]] # UKIDSS community.
username = 
password = 
community = ukidss.roe.ac.uk

[[leicester]] # Leicester community
username = 
password = 
community = uk.ac.le.star
"""

ipythonrc="""# -*- Mode: Shell-Script -*-  Not really, but shows comments correctly
#***************************************************************************
#
# Configuration file for ipython -- ipythonrc format
#
# The format of this file is one of 'key value' lines.
# Lines containing only whitespace at the beginning and then a # are ignored
# as comments. But comments can NOT be put on lines with data.
#***************************************************************************

# This is an example of a 'profile' file which includes a base file and adds
# some customizaton for a particular purpose.

# If this file is found in the user's ~/.ipython directory as ipythonrc-astrogr
id,
# it can be loaded by calling passing the '-profile astrogrid' (or '-p astrogri
d')
# option to IPython.

# load our basic configuration with generic options
include ipythonrc

# import ...
import_mod astrogrid

# from ... import ...
import_some astrogrid aghelp
import_some astrogrid acr
import_some astrogrid ConeSearch
import_some astrogrid SiapSearch
import_some astrogrid MySpace
import_some astrogrid Applications
import_some astrogrid DSA

execute print ""
execute print "  Welcome to the Astrogrid from Python environment."
execute print "  For more information, type aghelp()."
# execute if not acr._connected: acr.starthub()
"""

def cryptXOR(str2, pw):
    # create two streams in memory the size of the string str2
    # one stream to read from and the other to write the XOR crypted character to
    sr = StringIO.StringIO(str2)
    sw = StringIO.StringIO(str2)
    # make sure we start both streams at position zero (beginning)
    sr.seek(0)
    sw.seek(0)
    n = 0
    #str3 = ""  # test
    for k in range(len(str2)):
        # loop through password start to end and repeat
        if n >= len(pw) - 1:
            n = 0
        p = ord(pw[n])
        n += 1
        
        # read one character from stream sr
        c = sr.read(1)
        b = ord(c)
        # xor byte with password byte
        t = operator.xor(b, p)
        z = chr(t)
        # advance position to k in stream sw then write one character
        sw.seek(k)
        sw.write(z)
        #str3 += z  # test
    # reset stream sw to beginning
    sw.seek(0)
    res = sw.read()
    sr.close()
    sw.close()
    return res

def cryptconf():
    """Encrypt/decrypt configuration file"""
    home = os.path.expanduser('~')

    if sys.platform[:3] == 'win':
            conffile = os.path.join(home, '_python-acr')
    else:   
            conffile = os.path.join(home, '.python-acr')

    buffer = open(conffile,'rb').read()
    pw = getpass.getpass('Please insert your password: ')
    res = cryptXOR(buffer, pw)
    open(conffile, 'wb').write(res) 

def which(filename):
    """Find executable in PATH"""
    if not os.environ.has_key('PATH') or os.environ['PATH'] == '':
        p = os.defpath
    else:
        p = os.environ['PATH']

    pathlist = p.split (os.pathsep)

    for path in pathlist:
        f = os.path.join(path, filename)
        if os.access(f, os.X_OK):
            return f
    return None
    
def write_config():
    """Write current config values to configuration file."""
    if sys.platform[:3] == 'win':
        configfile=os.path.expanduser('~/_python-acr')
    else:
        configfile=os.path.expanduser('~/.python-acr')
        
    _config.write(configfile)
    
def install_ar(path):
    """Download the AR and instal it in some path. Update the configuration file."""
    
    filename = 'asr-2007.1.1-app.jar'
    url='http://www2.astrogrid.org/desktop/download/' + filename
    urllib.urlretrieve(url, os.path.join(path, filename))
    javapath = which('java')
    if not javapath: javapth='<path to your java executable>'
    print 'AR installed. In order to start the AR from Python, the following have been added'
    print 'lines to your .python-acr configuration file:'
    print ''
    print 'javapath = %s' % javapath
    print 'acrpath = %s' % os.path.join(path, filename)
    _config['javapath']=javapath
    _config['acrpath']=os.path.join(path, filename)
    write_config()
    
# ------------------------------------------------------------------------------------

if sys.platform[:3] == 'win':
	configfile=os.path.expanduser('~/_python-acr')
else:
	configfile=os.path.expanduser('~/.python-acr')

if not os.access(configfile, os.F_OK):
	open(configfile, 'w').write(python_acr)
	
# Try to set proper permissions in the file
try:
	fmode = stat.S_IMODE(os.stat(configfile)[stat.ST_MODE])
	cmode = stat.S_IWRITE + stat.S_IREAD
	if fmode<>cmode: os.chmod(configfile, cmode)
except:
	pass
	
# Now read the file
buffer = open(configfile, 'rb').read()
if md5.new(python_acr).hexdigest() == md5.new(buffer).hexdigest():
	print 'Default configuration file written in %s. Please edit it with your details.' % configfile
	sys.exit()
	
try:
	_config = ConfigObj(StringIO.StringIO(buffer))
except:
	print 'Your configuration file looks encrypted.'
	pw = getpass.getpass('Please type your password: ')
	buffer = cryptXOR(buffer, pw)
	_config = ConfigObj(StringIO.StringIO(buffer))
	

for k in ['debug', 'verbose', 'autologin', 'plastic', 'starthub']:
	_config[k] = _config.get(k, 'False') == 'True'
			
if not _config.has_key('community'): _config['community']={}


    