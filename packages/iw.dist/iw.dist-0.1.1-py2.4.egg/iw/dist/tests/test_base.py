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

from iw.dist.base import MCommand

class TestMCommand(unittest.TestCase):

    def test_get_pypirc(self):
        def _sort(el):
                key, value = el
                value = value.items()
                value.sort()
                return key, value

        wanted = [('acme-login', [('repository', 'http://example.org/'), 
                                  ('password', 'secret'), 
                                  ('realm', 'acme'), 
                                  ('username', 'tarek')]), 
                  ('plone-login', [('repository', 'http://plone.org/products'), 
                                   ('password', 'secret'), 
                                   ('realm', 'pypi'),
                                   ('username', 'tarek')]), 
                  ('server-login', [('repository', 'http://pypi.python.org/pypi'),
                                    ('password', 'secret'), 
                                    ('realm', 'pypi'), 
                                    ('username', 'tarek')])] 
        wanted.sort()
        wanted = [_sort(el) for el in wanted]
        old_home = os.environ['HOME']
        os.environ['HOME'] = os.path.dirname(__file__)
        try:
            reg = MCommand()
            servers = reg. _get_pypirc()
            servers = servers.items()
            servers.sort()
            servers = [_sort(el) for el in servers]
            self.assertEquals(servers, wanted)
        finally:
            os.environ['HOME'] = old_home

def test_suite():
    """returns the test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestMCommand))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

