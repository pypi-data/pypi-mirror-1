"""Tests for distutils.command.upload."""
import sys
import os
import unittest

from collective.dist.mupload import mupload
from distutils.core import Distribution

from distutils.tests import support
from collective.dist.tests.test_pypirc import PYPIRC, PyPIRCCommandTestCase


PYPIRC_NOPASSWORD = """\
[distutils]

index-servers =
    server1

[server1]
username:me
"""


class uploadTestCase(PyPIRCCommandTestCase):

    def test_finalize_options(self):

        # new format
        f = open(self.rc, 'w')
        f.write(PYPIRC)
        f.close()

        dist = Distribution()
        cmd = mupload(dist)
        cmd.finalize_options()
        for attr, waited in (('username', 'me'), ('password', 'secret'),
                             ('realm', 'pypi'),
                             ('repository', 'http://pypi.python.org/pypi')):
            self.assertEquals(getattr(cmd, attr), waited)


    def test_saved_password(self):
        # file with no password
        f = open(self.rc, 'w')
        f.write(PYPIRC_NOPASSWORD)
        f.close()

        # make sure it passes
        dist = Distribution()
        dist.password = ''   # Needed since in Python 2.4, Distribution class do not initialize the password attr

        #cmd = mupload(dist)
        #cmd.finalize_options()
        #self.assertEquals(cmd.password, None)

        # make sure we get it as well, if another command
        # initialized it at the dist level
        dist.password = 'xxx'
        cmd = mupload(dist)
        cmd.finalize_options()
        self.assertEquals(cmd.password, 'xxx')


def test_suite():
    return unittest.makeSuite(uploadTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
