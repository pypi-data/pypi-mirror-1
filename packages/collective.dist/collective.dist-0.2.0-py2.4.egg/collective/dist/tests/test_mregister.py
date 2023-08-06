"""Tests for distutils.command.register."""
import sys
import os
import unittest
from StringIO import StringIO

from collective.dist.mregister import mregister
from setuptools.dist import Distribution

from distutils.tests import support
from collective.dist.tests.test_pypirc import PYPIRC, PyPIRCCommandTestCase

import urllib2

data_sent = {}

class Opener(object):
    
    def open(self, req, data=None):
        if isinstance(req, str):
            assert req.startswith('http')
            return StringIO('ok')
        data_sent[req.get_host()] = (req.headers, req.data)

def build_opener(*auth):
    return Opener()

urllib2.build_opener = build_opener

class registerTestCase(PyPIRCCommandTestCase):

    def setUp(self):
        PyPIRCCommandTestCase.setUp(self)
        f = open(self.rc, 'w')
        f.write(PYPIRC)
        f.close()
        self.dist = Distribution()
        self.cmd = mregister(self.dist)
        
    def test_mregister(self):
        
        self.cmd.send_metadata()
        length = data_sent['pypi.python.org'][0]['Content-length']
        self.assertEquals(length, '1392')

    def test_get_non_default(self):
        # tests if we send data to the non default
        self.cmd.repository = 'server2'
        self.cmd.send_metadata()
        self.assert_('another.pypi' in data_sent)

        # tests if we send data to the non default
        import urllib2
        old = urllib2.HTTPPasswordMgr
        class _HTTPPasswordMgr:
            def add_password(self, realm, *args):
                urllib2._realm = realm
        urllib2.HTTPPasswordMgr = _HTTPPasswordMgr


        self.cmd.repository = 'server2'
        self.cmd.send_metadata()
        self.assert_('another.pypi' in data_sent)
        self.assertEquals(urllib2._realm, 'acme')
        urllib2.HTTPPasswordMgr = old
        delattr(urllib2, '_realm')

    def test_not_existing(self):
        # making sure we get an explicit message when the server 
        # does not exists in the .pypirc file
        self.cmd.repository = 'server128'
        self.assertRaises(ValueError, self.cmd.send_metadata)

    def test_creating_pypirc(self):
        # making sure we create a pypirc
        os.remove(self.cmd._get_rc_file())

        self.cmd.repository = 'pypi'

        # patching things to avoid interaction
        def _raw_input(msg=''):
            if msg == 'Save your login (y/N)?':
                return 'y'
            return '1'
        import getpass
        getpass.getpass = _raw_input
        func_globs = self.cmd.send_metadata.im_func.func_globals
        func_globs['raw_input'] = _raw_input

        # calling the register
        self.cmd.send_metadata()

        # now checking the created file
        content = open(self.cmd._get_rc_file()).read()
        content = content.replace(' ', '')
        wanted = """\
        [pypirc]
        servers = 
            pypi
                
        [pypi]
        username:1
        password:1""".strip()

        self.assertEquals(content.strip(), wanted.replace(' ', ''))

    def test_classifiers(self):
        # when calling the classifier with the contracted
        # -r option, it is not translated
        self.cmd.repository = 'server1' 
        self.cmd.classifiers()
        

def test_suite():
    return unittest.makeSuite(registerTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")

