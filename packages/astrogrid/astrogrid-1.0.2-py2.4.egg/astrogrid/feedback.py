
import os
import tempfile
import base64
import urllib, urllib2
import datetime

try:
	ed = os.environ['EDITOR']
except KeyError:
    if os.name == 'posix':
        ed = 'vi'  # the only one guaranteed to be there!
    else:
        ed = 'notepad' # same in Windows!


text = """Your email:
Subject:

text

"""

def calleditor(filename):
	os.system('%s %s' % (ed,filename))


def submit():
	print 'Please complete the next form using the editor (%s)' % ed
	print 'Press [Return]'; raw_input()
	fname=tempfile.mktemp()
	open(fname,'w').write(text)
	calleditor(fname)

	feedback = open(fname).read()
	now = datetime.datetime.now()
	feedback = 'Date: ' + now.strftime('%Y%m%dT%H:%M:%S') + '\n' + feedback
	os.unlink(fname)

	try:
		urllib2.urlopen('http://casu.ast.cam.ac.uk/ag/portal/server.py/feedback', urllib.urlencode({'data': feedback})).read()
		print 'Thanks for your feedback'
	except:
		pass
		