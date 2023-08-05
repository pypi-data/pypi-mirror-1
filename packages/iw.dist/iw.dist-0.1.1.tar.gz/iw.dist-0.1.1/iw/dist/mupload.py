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
""" mupload

    this command works like upload except that
    it make uploads on several sites
"""
import os
import urlparse
from setuptools.command.upload import upload

from base import MCommand

class mupload(upload, MCommand):

    description = "upload the distribution to several indexes"

    def finalize_options(self): 
        """reading the conf file"""
        self.conf = self._get_pypirc()
        if self.conf is None:
            upload.finalize_options()
        
    def upload_file(self, command, pyversion, filename):
        """upload file on several servers"""
        if self.conf is None:  
            upload.upload_file(self, command, pyversion, filename) 
            return

        for server in self.conf.values():
            host = server['repository']
            choice = raw_input(('Do you want to upload the package '
                                'at %s (y/N)? ' % host))
            if choice.lower() not in ('y', 'yes'):
                continue
            
            # XXX hack: setting attributes to avoid rewriting the whole
            # class
            self.repository = host
            self.username = server['username']
            self.password = server['password']
            # XXX not used for now
            #self.realm = server['realm']
            upload.upload_file(self, command, pyversion, filename)         

