.. contents::
.. sectnum::

.. raw:: html

   <p>&nbsp;</p>
   
You can access the services and tools provided by Astrogrid from several scripting/programming
languages. In this document we describe how this is done from Python. Python is a high level
programming language which is becoming very popular in astronomy.
   
.. image:: workbench_python.png
   :align: center

.. raw:: html

   <p style="font-size: smaller; color: #444; text-align: center">Notice the little Python logo on 
   the bottom right...</p>   
   
   
.. file: requirements.rst

Requirements
------------

//.. contents::

Python
~~~~~~

In order to access the Astrogrid services from Python you need a recent version of 
Python installed. Python versions 2.4 (released on November 30, 2004) and greater 
come with all needed libraries but the latest version of Python is recommended 
(2.5 released on September 19th, 2006). In order to know which python version you are
running you can type from the command line::

   python -c 'import sys; print sys.version'

If you do not have a version greater or equal to 2.4 then you will need to install a more
recent Python. Find below some instructions on installing Python in different system. 
More details are available in the 
`Beginners Guide Downloads Section <http://wiki.python.org/moin/BeginnersGuide/Download>`__.

**If you are running Windows** just go to the Python download page 
(http://www.python.org/download/) and choose Python 2.5 Windows Installer. 
By default Python will be installed in the directory C:\Python25. 

**If you use Linux** then Python is included in all main distributions by default. Refer to 
your package install instructions to install it if it is not already in your system. 
Generally something like ``apt-get install python`` or ``yum install python`` will be enough. 

**Mac OS X** comes with Python 2.3 installed, but you will need to use Python 2.4 or later. 
There are several ways of getting it:

* Fink Project (http://finkproject.org/). This is probably the best if you are used to Linux. 
  Together with Python and all additional packages you can install a whole load of unix tools.
* PythonMac (http://pythonmac.org/packages/)  
* You can also follow instructions in here: http://www.physics.usyd.edu.au/astrop/ausvoss/index.php/Main/InstallMacOSX
  
Learning Python
~~~~~~~~~~~~~~~

There are excelent resources in the web for learning python 
(e.g. the `Beginners Guide <http://wiki.python.org/moin/BeginnersGuide>`__). 
The Space Telescope has a Tutorial on using Python for Interactive Data Analysis (pdf_).

.. _pdf: http://stsdas.stsci.edu/perry/pydatatut.pdf

IPython
~~~~~~~

IPython (http://ipython.scipy.org) is an enhanced interactive shell for Python. You can
work with Python without this but then you will be missing a lot. Recommended package to install.

Additional Python Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~

Below some packages which are very useful and every astronomer thinking in using Python 
should install. 

* EasyInstall (http://peak.telecommunity.com/DevCenter/EasyInstall). This makes very easy
  to install python packages in any platform.
* numpy (http://scipy.org) is used to work with numeric arrays in Python. This is a highly
  recommended package to install.
* numarray (http://www.stsci.edu/resources/software_hardware/numarray) is being replaced by numpy 
  but it is still good to have around since many modules have not made the switch yet.
* pyfits (http://www.stsci.edu/resources/software_hardware/pyfits) is a module to work with fits 
  images and tables. Latest release comes with the possibility of using numpy or numarray.
* matplotlib (http://matplotlib.sourceforge.net/) to produce plots.

If you are using Linux, these packages are probably included in your distribution repository, 
use your package manager (e.g. yum or synaptic) to install them. For Mac OS X follow the 
links to the Fink Project or PythonMac. Windows users should go to the individual pages 
of the packages -- all of them have a binary windows download.

If you have EasyInstall then you can install most of these packages using something like::

   easy_install numpy

Astrogrid Client Runtime
~~~~~~~~~~~~~~~~~~~~~~~~

The Astrogrid Client Runtime (ACR) provides a XMLRPC interface to access the functions 
from Python. Just launching the Astrogrid Workbench provides the ACR connection. It is possible
to configure Python to launch ACR at start if it is not already running but this is still 
an experimetal feature and not discussed here.

Compiled HTML Help Viewer
~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to browse this documentation using a GUI interface (invoked by typing ``aghelp()`` in
the python interpreter) then you need a CHM viewer. Windows users do not need to install 
anything since it comes by default with the OS. For Linux and Mac users, follow the links below.

* Linux: GnoCHM at http://gnochm.sourceforge.net/
* Mac: Chmox at http://chmox.sourceforge.net/

Again linux users should be ready to go with just ``apt-get install gnochm`` or equivalent.

.. image:: chmox.jpg
   :align: center
   
.. file: install.rst

Installation and Configuration
------------------------------

//.. contents::

Installation
~~~~~~~~~~~~

If you have setuptools already installed you can skip this part; otherwise download `ez_setup.py <http://peak.telecommunity.com/dist/ez_setup.py>`_
and run it; this will download and install the appropriate setuptools egg for your Python version.

Then you just need to type::

   easy_install -f http://code.google.com/p/pyacr/downloads/list astrogrid

For more information using easy_install look at the 
`documentation <http://peak.telecommunity.com/DevCenter/EasyInstall>`__.

Configuration
~~~~~~~~~~~~~

This module expects a configuration in ``$HOME/.python-acr`` (or ``$HOME/_python-acr`` for Windows
Users). In order to create one just import the astrogrid module from python, it will automatically
detect that you do not have one and will create a skeleton one for you::

   python -c 'import astrogrid'

This default configuration file looks like::

  debug = True
  verbose = True
  autologin = True
  plastic = True
  
  [community]
  default=leicester
  
  [[leicester]]
  username = username1
  password = password1
  community = uk.ac.le.star
  
  [[ukidss]]
  username = username2
  password = password2
  community = ukidss.roe.ac.uk

where ``username[1,2]`` and ``password[1,2]`` are your particular credentials for logging into your
AstroGrid accounts. With this configuration you get maximum verbosity (debug, verbose) when running
your applications. Also you will not be asked about your login credentials since these will be read
from the configuration file when needed. In the second example you will be logged into in your
ukidss account by default but you can select the leicester account as well.

Make sure that the configuration file has right properties, i.e. it is only readable for the owner. 
In Unix you do ``chmod 0600 ~/.python_acr``. 

Encrypting the configuration file
'''''''''''''''''''''''''''''''''

For an extra layer of security you have the option to encrypt your configuration file. Of course
this means that you will be prompted for the password used to encrypt it when you use acr.
To do this, inside python::
//.. code-block:: Python

   from astrogrid.config import cryptconf
   cryptconf()
   
and type a password. The same command will decrypt a previously encrypted file.

Advanced options
~~~~~~~~~~~~~~~~

If you do not have root access or simply you do no want to install the module in the site-packages
directory you can specify an alternative path::

   # This is ~/.pydistutils.cfg
   [install]
   install_lib = ~/Library/Python/$py_version_short/site-packages
   install_scripts = ~/bin

Remember to set the ``PYTHONPATH`` variable to the correct directory.

.. file: gettingstarted.rst

Getting Started
---------------

In order to use AR from Python you need the AstroGrid workbench running.

Starting an interactive session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the module is installed, then just invoking python would be enough to have it available.

If you have IPython installed and copied the ``extras/ipythonrc-astrolib`` to your local
IPython configuration directory (``$HOME/.ipython/``) then you just need to type::

  ipython -p astrogrid
   
If you have installed the pylab package you can do a lot of plotting and numerical processing.
In this case you can type::

  ipython -pylab -p astrogrid

otherwise for normal python or ipython type::

  python
  from astrogrid import acr
  
.. file: howto.rst

How To...
~~~~~~~~~

.. file: howto_login.rst

Log In and Out
''''''''''''''

Once you have a configuration file as described above you can login
into your different accounts using::
//.. code-block:: Python

  # Login in the default account
  acr.login()
    
  # Login in your ukidss account
  acr.login('ukidss')
  
  # Login user particular credentials
  acr.login(username, password, community)

To log out simply type::
//.. code-block:: Python

  acr.logout()

.. file: howto_help.rst

Getting help
''''''''''''

Suppose that we want to perform a conesearch, so we first import the ConeSearch class::
//.. code-block:: Python

   from astrogrid import ConeSearch
   
You can get help about the usage of the class and its methods by typing::
//.. code-block:: Python

   help(ConeSearch)
   
If you have a CHM viewer installed (see above) you can get an enhanced page help by typing::
//.. code-block:: Python

   from astrogrid import aghelp
   aghelp()

.. file: howto_registry.rst

Query the Registry
''''''''''''''''''

The registry holds the information about all services available within the VO. Below some examples
on querying the registry for resources.
::
//.. code-block:: Python

   from astrogrid import Registry
   reg = Registry()
   
   # search for Cone services related to SDSS
   # and print their ids
   list = reg.searchCone('SDSS')
   print [p['id'] for p in list]
   
   # Print the description of service number 5 of the list
   print list[5]['content']['description']

.. file: howto_siap.rst

Perform a SIAP Query
''''''''''''''''''''

This are the basic lines to perform a SIAP search. For a more complete example
and link to a full working script look below in the examples section::
//.. code-block:: Python

   from astrogrid import SiapSearch
   siap = SiapSearch('ivo://roe.ac.uk/services/SIAPDR4-images')
   result = siap.execute(180.0, 2.0, 1.0)  

.. file: howto_dsa.rst

Query a catalogue using ADQL
''''''''''''''''''''''''''''

[Development::VOExplorer]
In order to query a service which provides ADQL capabilities we use the Data Set Access
class (DSA). The following example illustrates the basic commands to query the 2MASS PSC
catalogue::
//.. code-block:: Python

   from astrogrid import DSA
   db = DSA('ivo://wfau.roe.ac.uk/twomass-dsa/ceaApplication')
   app = db.query('SELECT TOP 10 * FROM twomass_psc AS x')
   
   app.status()
   
   result = app.results[0]
   
.. file: howto_myspace.rst

Work with MySpace
'''''''''''''''''

This is how you list the contents of your root directory of MySpace::
//.. code-block:: Python

   from astrogrid import MySpace
   m = MySpace()
   m.ls()
   
You can delete files or folders::
//.. code-block:: Python

   m.rm('#test/file.vot')
   m.rm('#test/', recursive=True)
   
and read file from MySpace::
//.. code-block:: Python

   img = m.readfile('#sdss/image.fits')

File names in MySpace always start with the hash key (#) or with 'ivo://'. For instance
when broadcasting a file to plastic listening applications::
//.. code-block:: Python

  # A file in local disk
  broadcast('image.fits')
  
  # A file in MySpace
  broadcast('#image.fits')

.. file: howto_plastic.rst

Send results to TOPCAT or Aladin
''''''''''''''''''''''''''''''''

If TOPCAT or Aladin (or any other Plastic listening application) are running t
hen you can send the results from your queries or tasks directly to them. This is how::
//.. code-block:: Python

   # Send a local file to Aladin
   acr.plastic.broadcast('image.fits', 'Aladin')
   
   # Send a file in MySpace to all applications
   acr.plastic.broadcast('#sdss/catalogue.vot')
   
   # Send the result from a cone search to Topcat
   result = cone.execute(250.0, 54.0, 0.3)
   acr.plastic.broadcast(result, 'Topcat')   

.. file: howto_background.rst

Run processes in the background
'''''''''''''''''''''''''''''''

Using IPython it is possible to run any process in the background. E.g.::
//.. code-block:: Python

   cone = ConeSearch("ivo://ned.ipac/Basic_Data_Near_Position")
   %bg cone.execute(180.0, 1.0, 0.1)
   %bg cone.execute(180.0, 2.0, 0.1)
   %bg cone.execute(180.0, 3.0, 1)
   
   jobs.status()
   Running jobs:
   2 : cone.execute(180.0, 3.0, 1)
   
   Completed jobs:
   0 : cone.execute(180.0, 1.0, 0.1)
   1 : cone.execute(180.0, 2.0, 0.1)
   
   jobs[1].status()
   'Completed'
   
   votable = jobs[1].result

.. file: api.rst

API Help
--------

The API is described `here <api.pdf>`__. The latest reference document is always included in the
``doc/api.pdf`` file in the source distribution.

.. file: examples.rst

Examples
--------

Below some examples which how some of the capabilities of the system.

.. file: examples_siap.rst

SIAP Image Search
~~~~~~~~~~~~~~~~~

The Simple Image Access Protocol allows to query a service for images which have observed 
a particular area of sky. The following example reads a list of object names from a file and 
uses the Sesame service to look at the coordinates of the object. Then for each of them, queries
the SDSS DR4 image service for images which have observed the object. The resultant votables are 
saved to a file for each object in the local disk.
::
//.. code-block:: Python

   # We read a list of object names from a file   
   # (see the completed script)
   
   # Initialize siap service search and name resolver
   siap = SiapSearch('ivo://roe.ac.uk/services/SIAPDR4-images')
   s = sesame()
   
   # Loop for each object of the list, query Vizier to get coordinates and execute
   # the SIAP search. The resultant VOTable is then saved to a file in the local
   # directory named after the object.
   for obj in objects:
        coords, ra, dec = s.resolve(obj)
        votable = siap.execute(ra, dec, 30.0/3600.0)
        open('%s.vot' % obj, 'w').write(votable)
        
One can substitute the last loop for the following one in order to save the output tables to
MySpace instead of local disk::
//.. code-block:: Python

   # Same loop as above. Now we save the VOTables to MySpace
   # We convert spaces to underscores in the saved filename due to MySpace complains
   # We do not overwrite existing files. We assume here that the username, password
   # and community credentials are specified in the configuration file (see docs)
   for obj in objects:
        coords, ra, dec = s.resolve(obj)
        ofile = '#siap/%s.vot' % obj.replace(' ','_')
        votable = siap.execute(ra, dec, 30.0/3600.0, saveAs=ofile)
   
Note that a cone search is done exactly in the same way using ConeSearch instead of SiapSearch.

File: `siapsearch.py <siapsearch.py>`__

.. file: examples_sextractor.rst

Extracting objects from an image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example we are going to show how to fill in the necessary parameters needed
to run a application and then submit it to the system.

Note that if one of the values is a pointer to a file then it is necessary to set the
'indirect' flag.

In this example the variables params, filter and config are strings containing the 
SExtractor configuration files (i.e. they are not the names of the files but the contents o the 
files) so it is not necesary to set the 'indirect' flag.
::
//.. code-block:: Python

   # Application ID. This is the name of the application we are going to run.
   # It can be obtained from a registry search.
   id = 'ivo://org.astrogrid/SExtractor'
   
   # We fill in the application parameters
   app = Applications(id)
   
   app.inputs['ANALYSIS_THRESH']['value']=1.5
   app.inputs['IMAGE_BAND']['value']='R'
   app.inputs['MAG_ZEROPOINT']['value']=25.0
   app.inputs['SEEING_FWHM']['value']=1.2
   
   app.inputs['PARAMETERS_NAME']['value']=params
   app.inputs['FILTER_NAME']['value']=filter
   app.inputs['config_file']['value']=config
   
   app.inputs['DetectionImage']['value'] = '#sextractor/image.fits'
   app.inputs['PhotoImage']['value'] = '#sextractor/image.fits'

   app.outputs['CATALOG_NAME']['value'] = '#sextractor/image_cat.fits'
   
   # We submit the application.
   task=app.submit()

   # We can poll the status of the application
   task.status()

It is possible to send the image and generated catalogue to Aladin::
//.. code-block:: Python

   from astrogrid.plastic import broadcast
   broadcast('#sextractor/image.fits')
   broadcast('#sextractor/image_cat.fits')

The result is shown in the figure below:

.. image:: aladin.jpg   
   :alt: Output of SExtractor on a 2MASS image
   :align: center
   
The complete script is in: `sextractor.py <sextractor.py>`__

.. file: examples_montage.rst

Running an application: Montage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this example we are going to create a mosaic from 2MASS images using Montage. First we
create an instance of the Applications class with the IVORN of the Montage application obtained 
from a registry search. The we fill in the app.inputs and app.outputs values and submit the 
application. Then we poll the status of the application until it is completed and we read the
result which has been saved to MySpace.
::
//.. code-block:: Python

   app = Applications('ivo://astrogrid.cam/Montage/prototype/2MASS-mosaic')
   
   # Now we fill in inputs...
   app.inputs['ra']['value'] = 312.75
   app.inputs['dec']['value'] = 44.37 
   app.inputs['size']['value'] = 0.3
   app.inputs['band']['value'] = 'K'
   
   # ...and outputs
   app.outputs['out.fits']['value'] = '#2mass/mosaic.fits'
   
   # Now submit the application
   task = app.submit() 
   
   # and check the status
   task.status() 
   
This example produced the following image:

.. image:: ic5070.jpg
   :alt: 2MASS image of IC5070 from Montage 
   :align: center

The complete script is available from: `montage_2mass.py <montage_2mass.py>`__

.. file: scripts.rst

Example Scripts
---------------

The following example scripts are available in the doc directory of the source distribution:

* siapsearch.py_: Runs a siap search on SDSS
* conesearch_2mass.py_: Executes a cone search to the 2MASS archive
* sextractor.py_: Extracts objects from image
* montage_2mass.py_: Produces a mosaic image from 2MASS

.. _siapsearch.py: siapsearch.py
.. _conesearch_2mass.py: conesearch_2mass.py
.. _sextractor.py: sextractor.py
.. _montage_2mass.py: montage_2mass.py

.. file: troubleshooting.rst

Troubleshooting
---------------

WARNING: Couldn't load the ACR config file - please start your ACR
  The AstroGrid workbench is not running.
  
ImportError: No module named _md5
  Your Python installation is broken. Make sure you have then OpenSSL libraries installed
  and that the ones used at compile time are the same as the ones used at runtime.
  
Error showing url: There is no default action associated with this location.
  When typing ``aghelp()`` this error appears if there is no application
  associated to open the HTML file. You will need to install GnoCHM and make
  sure that chm files are associated with it.

The required version of setuptools (>=0.6c6) is not available, and can't be installed while this script is running. Please install a more recent version first.
  Run ``python ez_setup.py`` from the source directory to install the required version of setuptools.

.. file: dictionary.rst

Appendix: Virtual Observatory Dictionary
----------------------------------------

Cone search
   A query which returns all objects within a defined distance from a particular position.
   
Registry
   This is the Google of the VO and holds information about all services published to the VO.
   
IVORN
   Who knows?

MySpace
   Virtual space storage.

Plastic
   Well...

SIAP
   Simple Image Access Protocol.
   More information in the `IVOA working draft <http://www.ivoa.net/Documents/latest/SIA.html>`__.
   
STAP
   Simple Time Access Protocol.
   
VOTable
   An XML format.


.. $LastChangedDate: 2007-06-18 12:22:21 +0100 (Mon, 18 Jun 2007) $
