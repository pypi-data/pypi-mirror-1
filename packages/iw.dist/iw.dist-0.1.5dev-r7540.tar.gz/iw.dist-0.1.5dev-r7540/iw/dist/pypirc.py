"""distutils.pypirc

Provides the PyPIRcCommand class, the base class for the command classes
that uses .pypirc in the distutils.command package.
"""
import os
from ConfigParser import ConfigParser

from distutils.core import Command 

DEFAULT_PYPIRC = """\
[pypirc]
servers = 
    pypi
    
[pypi]
username:%s
password:%s
"""

class PyPIRCCommand(Command):
    """Base command that knows how to handle the .pypirc file
    """
    DEFAULT_REPOSITORY = 'http://pypi.python.org/pypi'
    DEFAULT_REALM = 'pypi'
    repository = None
    realm = None

    def _get_rc_file(self):
        """Returns rc file path."""
        return os.path.join(self._get_home(), '.pypirc') 

    def _get_home(self):
        """Returns the home directory.
        
        home can differ depending on the platform"""
        home = os.getenv('HOME')    # linux style
        if home is None:
            home_drive = os.getenv('HOMEDRIVE') # win32 style
            home_path = os.getenv('HOMEPATH')
            if home_drive is not None and home_path is not None:
                return home_drive + home_path
        else:
            return home
        return os.curdir

    def _store_pypirc(self, username, password):
        """Creates a default .pypirc file."""
        rc = self._get_rc_file()
        f = open(rc, 'w')
        try:
            f.write(DEFAULT_PYPIRC % (username, password))
        finally:
            f.close()
        try:
            os.chmod(rc, 0600)
        except OSError:
            # should do something better here
            pass

    def _read_pypirc(self):
        """Reads the .pypirc file."""
        rc = self._get_rc_file()
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

