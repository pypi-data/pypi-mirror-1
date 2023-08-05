import unittest
import kforge.testunit
import kforge.unittesttest
import kforge.domtest
import kforge.utilstest
import kforge.dictionarytest
import kforge.apachetest
import kforge.accesscontroltest
import kforge.commandtest
import kforge.urltest
import kforge.plugintest
import kforge.applicationtest

def suite():
    suites = [
        kforge.unittesttest.suite(),
        kforge.domtest.suite(),
        kforge.utilstest.suite(),
        kforge.dictionarytest.suite(),
        kforge.apachetest.suite(),
        kforge.accesscontroltest.suite(),
        kforge.commandtest.suite(),
        kforge.urltest.suite(),
        kforge.plugintest.suite(),
        kforge.applicationtest.suite(),
    ]
    return unittest.TestSuite(suites)

