#!/usr/bin/python

import os
import cherrypy
import kid

class Root:
	@cherrypy.expose
	def index(self):
		page = kid.Template('templates/main.kid')
		return page.serialize(output='xhtml')
		
cherrypy.quickstart(Root())		