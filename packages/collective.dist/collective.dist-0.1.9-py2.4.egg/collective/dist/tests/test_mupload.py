"""Tests for distutils.command.upload."""
import sys
import os
import unittest

from collective.dist.mupload import mupload
from distutils.core import Distribution

from distutils.tests import support
from collective.dist.tests.test_pypirc import PYPIRC, PyPIRCCommandTestCase 

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

    
def test_suite():
    return unittest.makeSuite(uploadTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
