# modu
# Copyright (c) 2006-2010 Phil Christensen
# http://modu.bubblehouse.org
#
# $Id: __init__.py 1231 2010-02-04 05:27:06Z phil $
#
# See LICENSE for details

"""
Base package for itemdef discovery.
"""

import os, sys

__path__ = [os.path.abspath(os.path.join(x, 'modu', 'itemdefs')) for x in sys.path]

__all__ = []