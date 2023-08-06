# modusite
# Copyright (c) 2006-2010 Phil Christensen
# http://modu.bubblehouse.org
#
# $Id: release.py 1239 2010-02-05 19:06:48Z phil $
#

from modu.persist import storable

class Release(storable.Storable):
	def __init__(self):
		super(Release, self).__init__('release')
