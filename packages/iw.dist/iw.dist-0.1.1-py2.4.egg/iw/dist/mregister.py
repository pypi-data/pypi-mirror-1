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
""" mregister

    this command works like register excepts that
    it reads a .pypirc file that supports multiple
    servers
"""
import os
import urllib2
import urlparse
from ConfigParser import ConfigParser

from setuptools.command.register import register
from base import MCommand

class mregister(register, MCommand):

    description = "register the distribution with several indexes"

    def send_metadata(self):
        """allow multiple servers uploads"""
        conf = self._get_pypirc() 
        if conf is None:
            # let the register command do the work
            return register.send_metadata(self) 
       
        auth = urllib2.HTTPPasswordMgr()
        for server in conf.values():
            host = server['repository']
            choice = raw_input(('Do you want to register the package '
                                'metadata at %s (y/N)? ' % host))
            if choice.lower() not in ('y', 'yes'):
                continue
            username = server['username']
            password = server['password']
            realm = server['realm']
            root_host = urlparse.urlparse(host)[1]
            auth.add_password(realm, root_host, username, password)
            
            # XXX this is a hack to avoid rewriting the whole register
            # class
            self.repository = host
            code, result = self.post_to_server(self.build_post_data('submit'),
                                               auth)
            
            print 'Server %s response (%s): %s' % (host, code, result)

    def classifiers(self):
        """list classifiers on multiple servers"""
        conf = self._get_pypirc()
        if conf is None:
            return register.classifiers(self)
        for server in conf.values():
            self.repository = server['repository']
            register.classifiers(self)

