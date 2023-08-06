#!/usr/bin/python

import os
import xmlrpclib
from optparse import OptionParser
from configobj import ConfigObj

parser=OptionParser()

parser.add_option("--dir",
                  help="Destination directory.")
parser.add_option("--id",
                  help="Id.")                  
parser.add_option("--title", default='',
                  help="Title.") 
parser.add_option("--type", default='Document',
                  help="Plone Type.")
parser.add_option("--mtype", default='text/html',
                  help="Mime Type.")
parser.add_option("--state", default="draft",
                  help="State.")
parser.add_option("--creator", default='',
                  help="Creator.")                  

(options, args) = parser.parse_args()

config = ConfigObj(os.path.expanduser('~/.plone'))

d=config['astrogrid']
url="http://%(user)s:%(password)s@www2.astrogrid.org/"

if options.creator=='': options.creator = d['user']

s = xmlrpclib.ServerProxy(url % d)
res = s.doCreateDocument(options.dir, options.id, open(args[0],'r').read(), options.title,
                         '', options.type, options.mtype, options.state,
                         options.creator)
print res
