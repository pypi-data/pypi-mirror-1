import unittest
import tempfile

import os
import commands
import shutil
import sys

class InstallTest(unittest.TestCase):
    disable = True

    def setUp(self):
        """
        Basic setup.py install should install:
            code: sys.prefix/lib/python/site-packages
            data: sys.prefix/<whatever-pathes you give for installation>

        Under setuptools things are different ...
        """
        self.tmpDirPath = tempfile.mkdtemp()
        self.prefix = os.path.expanduser('~/kforge_install_test')
        self.libPath = os.path.join(self.prefix, 'lib/python/kforge')
        self.varPath = os.path.join(self.prefix, 'var')
        self.etcPath = os.path.join(self.prefix, 'etc')
        cmd = 'python setup.py install --home %s' % self.prefix
        status, output = commands.getstatusoutput(cmd)
        if status:
            self.cleanup()
            raise('Error on running install: %s' % output)
        # next item is to create an environment


    def cleanup(self):
        shutil.rmtree(self.tmpDirPath)
        self.uninstallKforge()

    def uninstallKforge(self):
        cmd1 = 'sudo rm -Rf %s' % self.libPath 
        os.system(cmd1)
        cmd2 = 'sudo rm -Rf %s' % self.varPath 
        cmd3 = 'sudo rm -Rf %s' % self.etcPath
        os.system(cmd2)
        os.system(cmd3)

    def tearDown(self):
        self.cleanup()

    def test_installWorked(self):
        self.failUnless(os.path.exists(self.libPath))
