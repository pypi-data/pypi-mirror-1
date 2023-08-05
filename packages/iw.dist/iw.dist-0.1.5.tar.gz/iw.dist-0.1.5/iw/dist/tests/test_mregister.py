"""Tests for distutils.command.register."""
import sys
import os
import unittest

from iw.dist.mregister import mregister
from distutils.core import Distribution

from distutils.tests import support
from iw.dist.tests.test_pypirc import PYPIRC, PyPIRCCommandTestCase

import urllib2

data_sent = {}

class Opener(object):
    
    def open(self, req):
        data_sent[req.get_host()] = (req.headers, req.data)

def build_opener(auth):
    return Opener()

urllib2.build_opener = build_opener

class registerTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        PyPIRCCommandTestCase.setUp(self)
        f = open(self.rc, 'w')
        f.write(PYPIRC)
        f.close()
        self.dist = Distribution()
        self.cmd = mregister(self.dist)
        
    def test_mregister(self):
        
        self.cmd.send_metadata()
        length = data_sent['pypi.python.org'][0]['Content-length']
        self.assertEquals(length, '1392')

    def test_get_non_default(self):
        # tests if we send data to the non default
        self.cmd.repository = 'server2'
        self.cmd.send_metadata()
        self.assert_('another.pypi' in data_sent)

def test_suite():
    return unittest.makeSuite(registerTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")

