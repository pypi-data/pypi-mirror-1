# Modu Sandbox
# Copyright (c) 2006-2010 Phil Christensen
# http://modu.bubblehouse.org
#
# $Id: page.py 1231 2010-02-04 05:27:06Z phil $
#
# See LICENSE for details

from modu.persist import storable

class Page(storable.Storable):
	def __init__(self):
		super(Page, self).__init__('page')
	
	def load_data(self, data):
		# Automatically convert binary data to string.
		if(hasattr(data['data'], 'tostring')):
			data['data'] = data['data'].tostring()
		super(Page, self).load_data(data)
