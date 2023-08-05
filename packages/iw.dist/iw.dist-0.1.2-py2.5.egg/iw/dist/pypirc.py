"""distutils.pypirc

Provides the PyPIRcCommand class, the base class for the command classes
that uses .pypirc in the distutils.command package.
"""
import os
from ConfigParser import ConfigParser

from distutils.core import Command 

class PyPIRCCommand(Command):

    DEFAULT_REPOSITORY = 'http://www.python.org/pypi'
    DEFAULT_REALM = 'pypi'
    repository = ''
    realm = ''

    def _store_pypirc(self, username, password):
        """stores the choice"""
        rc = os.path.join(os.environ['HOME'], '.pypirc')
        f = open(rc, 'w')
        try:
            f.write(('[pypirc]\n    servers = default\n '
                     '[default]\nusername:%s\npassword:%s\n') % \
                        (username, password))
        finally:
            f.close()
        try:
            os.chmod(rc, 0600)
        except:     # XXX ????
            pass

    def _read_pypirc(self):
        """Reads the .pypirc file."""
        if os.environ.has_key('HOME'): 
            rc = os.path.join(os.environ['HOME'], '.pypirc')
            if os.path.exists(rc):
                print 'Using PyPI login from %s' % rc
                repository = self.repository or self.DEFAULT_REPOSITORY
                realm = self.realm or self.DEFAULT_REALM

                config = ConfigParser()
                config.read(rc)
                sections = config.sections()
                
                if 'distutils' in sections:
                    # let's get the list of servers
                    index_servers = config.get('distutils', 'index-servers')
                    _servers = [server.strip() for server in 
                                index_servers.split('\n') 
                                if server.strip() != '']
                    if _servers == []:
                        # nothing set, let's try to get the defaut pypi
                        if 'pypi' in sections:
                            _servers = ['pypi']
                        else:
                            # the file is not properly defined, returning
                            # an empty dict
                            return {}
                    for server in _servers:
                        current = {'server': server}
                        current['username'] = config.get(server, 'username')
                        current['password'] = config.get(server, 'password')
                        
                        # optional params
                        for key, default in (('repository', 
                                              self.DEFAULT_REPOSITORY),
                                             ('realm', self.DEFAULT_REALM)):
                            if config.has_option(server, key):
                                current[key] = config.get(server, key)
                            else:
                                current[key] = default
                        if (current['server'] == repository or 
                            current['repository'] == repository):
                            return current
                elif 'server-login' in sections:
                    # old format
                    server = 'server-login'
                    if config.has_option(server, 'repository'):
                        repository = config.get(server, 'repository')
                    else:
                        repository = self.DEFAULT_REPOSITORY
                    return {'username': config.get(server, 'username'),
                            'password': config.get(server, 'password'),
                            'repository': repository,
                            'server': server,
                            'realm': self.DEFAULT_REALM}
                    
        return {}


