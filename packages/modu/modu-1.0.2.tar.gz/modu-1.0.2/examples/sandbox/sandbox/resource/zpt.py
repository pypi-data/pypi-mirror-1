# Modu Sandbox
# Copyright (c) 2006-2010 Phil Christensen
# http://modu.bubblehouse.org
#
# $Id: zpt.py 1231 2010-02-04 05:27:06Z phil $
#
# See LICENSE for details

from modu.web import resource

class Resource(resource.ZPTemplateResource):
	def prepare_content(self, req):
		self.set_slot('title', 'modu ZPT example page')
	
	def get_content_type(self, req):
		return 'text/html'
	
	def get_template(self, req):
		return 'zpt.html.tmpl' 
