# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Generic Test case for iw.dist doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import sys
import os

from iw.dist.mregister import mregister
from distutils.core import Distribution 
import urllib2

class Opener(object):
    def open(self, *args, **kw):
        pass

def _build_opener(auth_handler):
    return Opener()

urllib2.build_opener = _build_opener

class TestMRegister(unittest.TestCase):

    def test_send_metadata(self):
        def _raw_input(msg):
            return 'y'
        post_to_server = None
        dist = Distribution()
        old_home = os.environ['HOME']
        os.environ['HOME'] = os.path.dirname(__file__)
        try:
            reg = mregister(dist)
            # patching
            reg.send_metadata.im_func.func_globals['raw_input'] = _raw_input
            reg.send_metadata()
        finally:
            os.environ['HOME'] = old_home



def test_suite():
    """returns the test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMRegister))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

