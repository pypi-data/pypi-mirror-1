"""
The kforge.plugin unittest suite.
"""

import unittest
import os

from kforge.testunit import *
import kforge.plugin.basetest
import kforge.plugin.apacheconfigtest
import kforge.plugin.accesscontroltest
import kforge.plugin.wwwtest
import kforge.plugin.davtest
import kforge.plugin.svntest
import kforge.plugin.tractest
import kforge.plugin.mointest

def suite():
    suites = [
        kforge.plugin.basetest.suite(),
        kforge.plugin.apacheconfigtest.suite(),
        kforge.plugin.accesscontroltest.suite(),
        kforge.plugin.wwwtest.suite(),
        kforge.plugin.davtest.suite(),
        kforge.plugin.svntest.suite(),
        kforge.plugin.tractest.suite(),
        kforge.plugin.mointest.suite(),
    ]
    return unittest.TestSuite(suites)

