#!/usr/bin/python

import os, re

buffer = open('doc.rst').readlines()
fptr = None

for line in buffer:
	if re.compile('.. file:').match(line):
		ofile = re.compile('.. file: (\S+)').search(line).group(1)
		if fptr: fptr.close()
		fptr = open(os.path.join('help', ofile), 'w')
		continue
		
	if line.find('//')==0:
		line ='%s' % line[2:]

	if fptr: fptr.write(line)
	
		
		
