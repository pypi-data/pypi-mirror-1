"""Tests for distutils.pypirc.pypirc."""
import sys
import os
import unittest

from collective.dist.core import PyPIRCCommand
from setuptools.dist import Distribution

from distutils.tests import support

PYPIRC = """\
[distutils]

index-servers =
    server1
    server2

[server1]
username:me
password:secret

[server2]
username:meagain
password: secret
realm:acme
repository:http://another.pypi/
"""

PYPIRC_OLD = """\
[server-login]
username:tarek
password:secret
"""

SETUP_CFG = """\
[distutils]
index-servers =
    server3

[server3]
username:gawel
password: pipi
"""

class PyPIRCCommandTestCase(support.TempdirManager,
                            support.LoggingSilencer,
                            unittest.TestCase):

    def setUp(self):
        """Patches the environment."""
        if os.environ.has_key('HOME'):
            self._old_home = os.environ['HOME']
        else:
            self._old_home = None
        curdir = os.path.dirname(__file__)
        os.environ['HOME'] = curdir
        self.rc = os.path.join(curdir, '.pypirc')
        self.setup_cfg = os.path.join(curdir, 'setup.cfg')
        self.dist = Distribution()

        class command(PyPIRCCommand):
            def __init__(self, dist):
                PyPIRCCommand.__init__(self, dist)
            def initialize_options(self):
                pass
            finalize_options = initialize_options

        self._cmd = command

    def tearDown(self):
        """Removes the patch."""
        if self._old_home is None:
            del os.environ['HOME']
        else:
            os.environ['HOME'] = self._old_home
        if os.path.exists(self.rc):
            os.remove(self.rc)
        if os.path.exists(self.setup_cfg):
            os.remove(self.setup_cfg)

    def test_server_registration(self):
        # This test makes sure PyPIRCCommand knows how to:
        # 1. handle several sections in .pypirc
        # 2. handle the old format

        # new format
        f = open(self.rc, 'w')
        try:
            f.write(PYPIRC)
        finally:
            f.close()

        cmd = self._cmd(self.dist)
        config = cmd._read_pypirc()

        config = config.items()
        config.sort()
        waited = [('password', 'secret'), ('realm', 'pypi'),
                  ('repository', 'http://pypi.python.org/pypi'),
                  ('server', 'server1'), ('username', 'me')]
        self.assertEquals(config, waited)

        # old format
        f = open(self.rc, 'w')
        f.write(PYPIRC_OLD)
        f.close()

        config = cmd._read_pypirc()
        config = config.items()
        config.sort()
        waited = [('password', 'secret'), ('realm', 'pypi'),
                  ('repository', 'http://pypi.python.org/pypi'),
                  ('server', 'server-login'), ('username', 'tarek')]
        self.assertEquals(config, waited)

    def test_setup_cfg(self):

        # assume that we are in a test directory
        pwd = os.getcwd()
        os.chdir(os.environ['HOME'])

        # write setup.cfg
        f = open(self.setup_cfg, 'w')
        f.write(SETUP_CFG)
        f.close()

        cmd = self._cmd(self.dist)
        config = cmd._read_pypirc()
        config = config.items()
        config.sort()

        waited = [('password', 'pipi'), ('realm', 'pypi'),
                  ('repository', 'http://pypi.python.org/pypi'),
                  ('server', 'server3'), ('username', 'gawel')]
        self.assertEquals(config, waited)

        # assume that the setup.cfg override the .pypirc

        # write .pypirc
        f = open(self.rc , 'w')
        f.write(PYPIRC)
        f.close()

        cmd = self._cmd(self.dist)
        config = cmd._read_pypirc()
        config = config.items()
        config.sort()

        waited = [('password', 'pipi'), ('realm', 'pypi'),
                  ('repository', 'http://pypi.python.org/pypi'),
                  ('server', 'server3'), ('username', 'gawel')]
        self.assertEquals(config, waited)

        os.chdir(pwd)

    def test_repository_in_args(self):
        # make sure the -r option is always caught

        sys.argv.extend(['-r', 'toto'])
        try:
            cmd = PyPIRCCommand(self.dist)
            cmd.finalize_options()
            self.assertEquals(cmd.repository, 'toto')
        finally:
            sys.argv = sys.argv[:-2]

def test_suite():
    return unittest.makeSuite(PyPIRCCommandTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
