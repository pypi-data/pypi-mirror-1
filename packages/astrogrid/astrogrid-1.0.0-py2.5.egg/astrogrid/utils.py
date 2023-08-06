"""
Several applications.
"""
__id__ = '$Id: utils.py 97 2007-05-29 15:51:00Z eddie $'
__docformat__ = 'restructuredtext en'


import os, urlparse, tempfile
import VOTable
from applications import Applications
from astrogrid import acr
from decorators import deprecated

try:
    import pyfits
    has_pyfits = True
except:
    has_pyfits = False

def mkURI(input) :
    if input[:6]=='ivo://':
        return input
    elif input[0] == '#' : # a short-cut notation for user's myspace - make absolute
        return acr.astrogrid.myspace.getHome() + input[1:]
    
    currentDir = os.getcwd() + os.sep
    baseURI = urlparse.urlunsplit(["file","",currentDir,"",""])
    return urlparse.urljoin(baseURI,input) + os.sep

def read_votable(table, ofmt='votable'):
    """
    Read a votable string or local file and returns a VOTable or FITS structure.
    
    :Parameters:
       table : str
          string containing the votable or file in the local disk. If the file is in 
          MySpace, first read the file and then use this routine.
          
    :Keywords:
       ofmt : str
           Output format (votable|fits). Default: votable
    
    """
    ext={'votable': '.vot', 'fits': '.fits'}
    ifmt = 'votable'
    
    if table[:5] == '<?xml': # This is an inlined table
        tmpFile = tempfile.mktemp(".vot")
        open(tmpFile,'w').write(table)
        remove_tmpfile = True
    else:
        tmpFile = table
        remove_tmpfile = False
                
    tmpFile2 = tempfile.mktemp(ext[ofmt])

    acr.util.tables.convertFiles(mkURI(tmpFile), ifmt, mkURI(tmpFile2), ofmt)
        
    if ofmt=='votable':
        vot = VOTable.VOTable()
        vot.parseText(open(tmpFile2).read())
        os.unlink(tmpFile2)
    elif ofmt=='fits':
        if has_pyfits:
            vot = pyfits.open(tmpFile2)
            os.unlink(tmpFile2)
        else:
            vot = open(tmpFile2).read()
            os.unlink(tmpFile2)
            
    if remove_tmpfile: os.unlink(tmpFile)
    
    return vot

def browserview(vot):
    """
    Displays a votable as an HTML document in the system browser

    :Parameters:
      vot
        votable as a string

    """
    
    vot = acr.util.tables.convert(vot, 'votable', 'votable')
    
    tmpFile = tempfile.mktemp(".vot")
    open(tmpFile,'w').write(vot)
    tmp1 = urlparse.urlunsplit(['file','',os.path.abspath(tmpFile),'',''])
    
    tmpFile = tempfile.mktemp(".html")
    tmp2 = urlparse.urlunsplit(['file','',os.path.abspath(tmpFile),'',''])
    
    acr.util.tables.convertFiles(tmp1, "votable", tmp2, "html")
    acr.system.browser.openURL(tmp2)


def convertfile(ifile, ofile, ifmt='votable', ofmt='fits'):
    """
    Convert a file from one format to another. Both files are in the local disk.
    To convert a file which is in MySpace, either save it to local disk or use
    MySpace.convertfile.

    :Parameters:
      ifile : str
        input file
      ofile : str
        output file

    :Keywords:
      ifmt : str
        format of input file. Default: votable
      ofmt : str
        format of output file. Default: fits

    """
    f1 = urlparse.urlunsplit(['file','',os.path.abspath(ifile),'',''])
    f2 = urlparse.urlunsplit(['file','',os.path.abspath(ofile),'',''])
    res = acr.util.tables.convertFiles(f1, ifmt, f2, ofmt)
    return res == 'OK'
    
# For compatibility
@deprecated
def broadcast(*args, **kwargs):
	return acr.plastic.broadcast(*args, **kwargs)

def tmatch2(in1, in2, out,  matcher='1and2'):
    """
    Cross match two tables (stored in MySpace)

    :Parameters:
      in1 : str
        input table 1
      in2 : str
        input table 2
      out : str
        output tble

    :Keywords:
      matcher : str
        type of match
    """
    
    app = Applications()
    struct = app.template('ivo://starlink.ac.uk/stilts','tmatch2')
    inputs = struct['input']
    outputs = struct['output']

    inputs['tmatch2_in1']['value']=in1
    inputs['tmatch2_in2']['value']=in2

    outputs['output']['value'] = out

    applications.convertStructToDocument(struct)
    applications.validate(doc)
    applications.submit
