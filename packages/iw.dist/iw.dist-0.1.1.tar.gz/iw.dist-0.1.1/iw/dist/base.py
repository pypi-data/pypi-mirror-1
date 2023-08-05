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
""" provides a .pypirc reader for multiple servers
"""
import os
from ConfigParser import ConfigParser

class MCommand(object):

    DEFAULT_REALM = "pypi"
    DEFAULT_REPOSITORY = "http://pypi.python.org/pypi"

    def _get_pypirc(self):
        """get the pypirc file"""
        if os.environ.has_key('HOME'): 
            rc = os.path.join(os.environ['HOME'], '.pypirc')
            if os.path.exists(rc):
                print 'Using PyPI login from %s' % rc
                config = ConfigParser()
                config.read(rc)
                # make a dict out of the file
                servers = {}
                for section in config.sections():
                    current = {'username': config.get(section, 'username'),
                               'password': config.get(section, 'password')}

                    for key, default in (('repository', self.DEFAULT_REPOSITORY),
                                         ('realm', self.DEFAULT_REALM)):
                        if config.has_option(section, key):
                            current[key] = config.get(section, key)
                        else:
                            current[key] = default

                    servers[section] = current
                
                return servers    
        return None

