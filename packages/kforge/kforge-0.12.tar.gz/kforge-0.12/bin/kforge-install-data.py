#!/usr/bin/env python
# Extract data (templates etc) from eggs and install in appropriate locations

import os
import shutil

import pkg_resources
class InstallData(object):

    def __init__(self, base_path, verbose=True):
        self.base_path = base_path
        self.verbose = verbose

    def execute(self):
        self.install_config_template()
        self.install_django_templates()
        self.install_media()

    def install_config_template(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'), 'etc/kforge.conf.new')
        dest = os.path.join(self.base_path, 'kforge.conf.new')
        shutil.copy(filename, dest)

    def install_config_template(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'src/kforge/django/templates')
        dest = os.path.join(self.base_path, 'templates')
        shutil.copytree(filename, dest)

    def install_config_media(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'src/kforge/django/media')
        dest = os.path.join(self.base_path, 'media')
        shutil.copytree(filename, dest)

import tempfile
class TestInstallData(object):
    
    def setup_class(self):
        self.base_path = tempfile.mkdtemp()
        self.installer = InstallData(self.base_path)
        self.installer.execute()

    def teardown_class(self):
        shutil.rmtree(self.base_path)

    def test_01(self):
        kforgeconf = os.path.join(self.base_path, 'kforge.conf.new')
        assert os.path.exists(kforgeconf)

    def test_02(self):
        dest = os.path.join(self.base_path, 'templates')
        dest2 = os.path.join(self.base_path, 'templates', 'kui', 'master.html')
        assert os.path.exists(dest)
        assert os.path.exists(dest2)

if __name__ == '__main__':
    import optparse
    usage  = \
'''usage: %prog <base-directory>'
'''
    parser = OptionParser(usage)
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help(0)
        sys.exit(1)
    installer = InstallData(args[0])
    installer.execute()
