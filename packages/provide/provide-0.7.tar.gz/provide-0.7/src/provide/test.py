import unittest
import provide.domtest
import provide.plugintest
import provide.djangotest
import provide.locatortest
import provide.configwritertest

def suite():
    suites = [
        provide.domtest.suite(),
#        provide.plugintest.suite(),
        provide.djangotest.suite(),
        provide.locatortest.suite(),
        provide.configwritertest.suite(),
    ]
    return unittest.TestSuite(suites)

