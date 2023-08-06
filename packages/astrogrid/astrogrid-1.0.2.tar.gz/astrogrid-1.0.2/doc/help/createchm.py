#!/usr/bin/python

import glob
import optparse
import os
import sys

__version__ = 0.2

# ---------------------------------------------------------------------------
# template for HHC (contents file)

HHC_HEADER = """\
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
<HEAD>
<meta name="GENERATOR" content="rst2chm v%s">
<!-- Sitemap 1.0 -->
</HEAD><BODY>
<OBJECT type="text/site properties">
	<param name="Auto Generated" value="No">
</OBJECT>
""" % __version__

HHC_ITEM = """\
<LI><OBJECT type="text/sitemap">
    <param name="Name" value="%(name)s">
    <param name="Local" value="%(href)s">
    <param name="ImageNumber" value="%(imageno)s">
</OBJECT></LI>
"""

HHC_FOOTER = """\
</BODY></HTML>
"""

HHP_TEMPLATE = """\
[OPTIONS]
Compatibility=1.1 or later
Compiled file=%(chm_file)s
Contents file=%(hhc_file)s
Default topic=%(default_topic)s
Display compile progress=%(display_compile_progress)s
Full-text search=%(full_text_search_on)s
Language=%(language)s
Title=%(title)s

[FILES]
%(files)s

[INFOTYPES]
"""

LANGUAGES = {
    'af': '0x0436 Afrikaans',
    'de': '0x0407 German (Germany)',
    'en': '0x0409 English (United States)',
    'es': '0x040a Spanish (Traditional Sort)',
    'fr': '0x040c French (France)',
    'it': '0x0410 Italian',
    'ru': '0x0419 Russian',
    'sk': '0x041b Slovak',
    'sv': '0x041d Swedish',
    'gb': '0x0809 English (United Kingdom)',
}

imageno = {'doc': 11, 'edoc': 11, 'book': 1, 'link': 11, 'elink': 11, 'file': 41, 'folder': 5,
           'efile': 41}

htm_files = [ ['doc', 'home.htm', ''], 
              ['doc', 'requirements.htm', ''],
#              ['link', 'requirements.htm#python', 'Python'],
#              ['link', 'requirements.htm#ipython', 'IPython'],
#              ['link', 'requirements.htm#additional-python-packages', 'Additional Python Packages'],
#              ['elink', 'requirements.htm#astrogrid-client-runtime', 'Astrogrid Runtime'],
              ['doc', 'install.htm', ''], 
		      ['doc', 'gettingstarted.htm', ''],
		      ['book', 'howto.htm', ''],
		      ['doc', 'howto_login.htm', ''],
                      ['doc', 'howto_myspace.htm', ''],
		      ['doc', 'howto_registry.htm', ''],
		      ['doc', 'howto_siap.htm', ''],
		      ['doc', 'howto_plastic.htm', ''],
		      ['edoc', 'howto_background.htm', ''],
		      ['book', 'api\\astrogrid-module.html', 'API Documentation'],
		      ['doc', 'api\\astrogrid.applications.Applications-class.html', 'Applications'],
		      ['doc', 'api\\astrogrid.community.Community-class.html', 'Community'],
		      ['doc', 'api\\astrogrid.cone.ConeSearch-class.html', 'ConeSearch'],
		      ['doc', 'api\\astrogrid.config.Configuration-class.html', 'Configuration'],
		      ['doc', 'api\\astrogrid.myspace.MySpace-class.html', 'MySpace'],
		      ['doc', 'api\\astrogrid.registry.Registry-class.html', 'Registry'],
		      ['doc', 'api\\astrogrid.siap.SiapSearch-class.html', 'SiapSearch'],	
		      ['edoc', 'api\\astrogrid.stap.StapSearch-class.html', 'StapSearch'],
		      ['book', 'examples.htm', ''], 
		      ['doc', 'examples_siap.htm', ''], 
		      ['doc', 'examples_sextractor.htm', ''],
		      ['edoc', 'examples_montage.htm', ''],
		      ['folder', 'scripts.htm', ''],
		      ['file', 'conesearch_2mass.py.html', 'conesearch_2mass.py'],
		      ['file', 'siapsearch.py.html', 'siasearch.py'],
		      ['file', 'sextractor.py.html', 'sextractor.py'],
		      ['efile', 'montage_2mass.py.html', 'montage_2mass.py'],
		      ['doc', 'dictionary.htm', '']
		    ]


f = open('astrogrid.hhc', 'w')
print >> f, HHC_HEADER
print >> f, '<UL>'

for item in htm_files:
    #if item[0]=='file': continue
    name = item[2]
    if name=='':
        buffer=open(item[1]).read()
        i1, i2 = buffer.find('<title>'), buffer.find('</title>')
        name=buffer[i1+7:i2]
        
    href = item[1]
    print >> f, HHC_ITEM % {'name': name, 'href': href, 'imageno': imageno[item[0]]}
    if item[0] in ('book', 'folder'): print >> f, '<UL>'
    if item[0] in ('edoc', 'elink', 'efile'): print >> f, '</UL>'

print >> f, '</UL>'
print >> f, HHC_FOOTER
f.close()

settings = {'chm_file': 'astrogrid.chm',
            'hhc_file': 'astrogrid.hhc',
            'default_topic': 'home.htm',
            'display_compile_progress': 'Yes',
            'full_text_search_on': 'Yes',
            'language': LANGUAGES['gb'],
            'title': 'Astrogrid Python Module',
            'files': '\n'.join([f[1] for f in htm_files])}

f = open('astrogrid.hhp', 'w')
print >> f, HHP_TEMPLATE % settings
f.close()


