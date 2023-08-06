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
        try:
            self.installTemplates()
        except Exception, inst:
            msg = "Couldn't install template files: %s" % str(inst)
            raise Exception(msg)
        try:
            self.installMedia()
        except Exception, inst:
            msg = "Couldn't install media files: %s" % str(inst)
            raise Exception(msg)
        #self.installHtdocs()

    def installTemplates(self):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'kforge/django/templates/kui')
        templatesPath = self.dictionary[self.dictionary.words.DJANGO_TEMPLATES_DIR]
        templatesPath = os.path.normpath(templatesPath)
        if os.path.exists(templatesPath):
            print "Skipping templates: The templates folder already exists: %s" % templatesPath
        else:
            templatesPathParent = os.path.dirname(templatesPath)
            self.assertFolder(templatesPathParent)
            shutil.copytree(filename, templatesPath)

    def installMedia(self):
        mediaResourcePath = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'kforge/htdocs/media')
        mediaPath = self.dictionary[self.dictionary.words.MEDIA_PATH]
        mediaPath = os.path.normpath(mediaPath)
        if os.path.exists(mediaPath):
            print "Skipping media: The media folder already exists: %s" % mediaPath
        else:
            mediaPathParent = os.path.dirname(mediaPath)
            self.assertFolder(mediaPathParent)
            shutil.copytree(mediaResourcePath, mediaPath)

    def installHtdocs(self):
        # Todo: Just put this stuff inside media.
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('kforge'),
            'kforge/htdocs/project')
        mediaPath = self.dictionary[self.dictionary.words.MEDIA_PATH]
        htdocsPath = os.path.join(mediaPath, 'project')
        htdocsPath = os.path.normpath(htdocsPath)
        htdocsPathParent = os.path.dirname(htdocsPath)
        if not os.path.exists(htdocsPathParent):
            os.makedirs(htdocsPathParent)
        shutil.copytree(filename, htdocsPath)

    def assertFolder(self, folderPath):
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

