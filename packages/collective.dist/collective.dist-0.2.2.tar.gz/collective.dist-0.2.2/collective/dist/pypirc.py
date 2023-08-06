"""distutils.pypirc

Provides the PyPIRcCommand class, the base class for the command classes
that uses .pypirc in the distutils.command package.
"""
import os
import sys
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
        return os.path.join(os.path.expanduser('~'), '.pypirc')

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
        """Reads the .pypirc file and setup.cfg if any."""
        rc = self._get_rc_file()
        files = [f for f in [rc, 'setup.cfg'] if os.path.exists(f)]
        if files:
            repository = self.repository or self.DEFAULT_REPOSITORY
            realm = self.realm or self.DEFAULT_REALM

            print 'Using PyPI login from %s' % ', '.join(files)
            config = ConfigParser()
            config.read(files)

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

                    # optional params
                    for key, default in (('repository',
                                          self.DEFAULT_REPOSITORY),
                                         ('realm', self.DEFAULT_REALM),
                                         ('password', None)):  # password are now an optional param
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

    def initialize_options(self):
        self.repository = None
        self.realm = None

    def finalize_options(self):
        # we need to make sure the repository is not provided
        # after another command in the arguments
        # if so, we need to get it
        if '-r' in sys.argv or '--repository' in sys.argv:
            if '-r' in sys.argv:
                 pos = sys.argv.index('-r') + 1
            else:
                pos = sys.argv.index('--repository') + 1
            if len(sys.argv) > pos:
                self.repository = sys.argv[pos]

        if self.repository is None:
            self.repository = self.DEFAULT_REPOSITORY
        if self.realm is None:
            self.realm = self.DEFAULT_REALM

