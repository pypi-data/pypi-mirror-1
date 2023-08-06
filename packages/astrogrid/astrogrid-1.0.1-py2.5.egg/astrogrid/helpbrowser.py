#!/usr/bin/python

__id__ = '$Id: helpbrowser.py 97 2007-05-29 15:51:00Z eddie $'

import os
import sys

def open(filename):
	if sys.platform[:3] == 'win':
		res = os.startfile(filename)
	elif sys.platform == 'darwin':
		res = os.system('open %s' % filename)
	elif sys.platform[:5] == 'linux':
		for c in ['gnome-open', 'kde-open', 'exo-open']:
			res = os.system('%s %s 2>/dev/null' % (c, filename))
			if res:	break
			
def aghelp():
	helpfile = os.path.join(os.path.dirname(__file__), 'astrogrid.chm')
	open(helpfile)
	

