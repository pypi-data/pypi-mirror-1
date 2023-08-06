#!/usr/bin/env python
# Extract data (templates etc) from eggs and install in appropriate locations

## TODO: default to share/kforge for base
## TODO: use config file to install necessary data (templates etc)

import os
import shutil

import pkg_resources

def get_config_template():
    # special case needed to bootstrap
    filename = pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('kforge'),
        'kforge/etc/kforge.conf.new')
    config = file(filename).read()
    return config

class InstallData(object):

    def __init__(self, verbose=True):
        import kforge.dictionary
        self.dictionary = kforge.dictionary.SystemDictionary()
        self.verbose = verbose

    def execute(self):
        self.install_django_templates()
        self.install_media()
        self.install_htdocs()

    def install_django_templates(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'kforge/django/templates/kui')
        dest = self.dictionary['django.templates_dir']
        dest = os.path.normpath(dest)
        destParent = os.path.dirname(dest)
        if not os.path.exists(destParent):
            os.makedirs(destParent)
        shutil.copytree(filename, dest)

    def install_media(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'kforge/htdocs/media')
        dest = self.dictionary['www.media_root']
        dest = os.path.normpath(dest)
        destParent = os.path.dirname(dest)
        if not os.path.exists(destParent):
            os.makedirs(destParent)
        shutil.copytree(filename, dest)

    def install_htdocs(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'kforge/htdocs/project')
        dest = os.path.join(self.dictionary['www.media_root'], 'project')
        dest = os.path.normpath(dest)
        destParent = os.path.dirname(dest)
        if not os.path.exists(destParent):
            os.makedirs(destParent)
        shutil.copytree(filename, dest)

