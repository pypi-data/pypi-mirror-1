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

from iw.dist.mupload import mupload
from distutils.core import Distribution 

import httplib

class Response(object):
    status = 200
    reason = 'OK'

class _HTTPConnection(object):
    def __init__(self, netloc):
        pass

    def connect(self):
        pass

    def putrequest(self, *args, **kw):
        pass

    putheader = putrequest
    endheaders = putrequest
    send = putrequest
    
    def getresponse(self):
        return Response()

httplib.HTTPConnection = _HTTPConnection

class TestMUpload(unittest.TestCase):

    def test_finalize_options(self):
        def _raw_input(msg):
            return 'y'
        post_to_server = None
        dist = Distribution()
        old_home = os.environ['HOME']
        os.environ['HOME'] = os.path.dirname(__file__)
        try:
            reg = mupload(dist)
            # patching
            for func_ in (reg.finalize_options, reg.upload_file):
                func_.im_func.func_globals['raw_input'] = _raw_input
            reg.finalize_options()
            path = os.path.join(os.path.dirname(__file__), '.pypirc')
            reg.upload_file('xxx', '', path)
        finally:
            os.environ['HOME'] = old_home

def test_suite():
    """returns the test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMUpload))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

