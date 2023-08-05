#!/usr/bin/env python
#
# KnowledgeForge distutils setup.py
#
from distutils.core import setup
from setup_helper import *
import sys
sys.path.insert(0, './src')
from kforge import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))

setup(
    name='kforge',
    version=__version__,
    author='Open Knowledge Foundation',
    author_email='kforge-dev@lists.okfn.org',
    license='GPL',
    url='http://www.kforgeproject.com/',
    download_url = 'http://www.kforgeproject.com/files/kforge-%s.tar.gz' % __version__,
    description='Collaborative development environment for software or knowledge',
    long_description =\
"""
KForge is an open-source (GPL) system for managing software and knowledge projects. It re-uses existing best-of-breed tools such as a versioned storage (subversion), a tracker (trac), and wiki (trac or moinmoin), integrating them with the system's own facilities (projects, users, permissions etc). KForge also provides a complete web interface for project administration as well as a fully-developed plugin system so that new services and features can be easily added.
""",
    
    package_dir={'': 'src'},
    packages= getPackages(os.path.join(basePath, 'src')),
    
    scripts= getScripts(basePath, 'bin'),
    data_files=[
        ('share/kforge/etc', ['etc/kforge.conf.new']),
        ] \
        + getDataFiles('share/kforge/www/media', basePath, 'src/kforge/django/media') \
        + getDataFiles('share/kforge/www/project', basePath, 'www/project') \
        + getDataFiles('share/kforge/templates', basePath, 'src/kforge/django/templates')
              
)
