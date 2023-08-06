import unittest
from provide.configwriter import ConfigWriter

def suite():
    suites = [
        unittest.makeSuite(TestConfigWriterNull),
        unittest.makeSuite(TestConfigWriterValueSubst),
        unittest.makeSuite(TestConfigWriterNoChange),
        unittest.makeSuite(TestConfigWriterAppendValue),
        unittest.makeSuite(TestConfigWriterAppendSection),
    ]
    return unittest.TestSuite(suites)


class ConfigWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.configWriter = ConfigWriter()

    def test(self):
        self.configWriter.updateLines(self.configLines, self.updateLines)
        self.failUnlessEqual(self.configWriter.newLines, self.expectedLines)


class TestConfigWriterNull(ConfigWriterTestCase):
    configLines = []
    updateLines = []
    expectedLines = []

class TestConfigWriterNoChange(ConfigWriterTestCase):
    configLines = ["#Some comment","[DEFAULT]","name1 = value1","","[section1]","name1 = value2"]
    updateLines = []
    expectedLines = ["#Some comment","[DEFAULT]","name1 = value1","","[section1]","name1 = value2"]

class TestConfigWriterValueSubst(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","name1=value1","","[section1]","name1= value2"]
    updateLines = ["[DEFAULT]","name1=value3","[section1]","name1=value4"]
    expectedLines = ["[DEFAULT]","name1 = value3","","[section1]","name1 = value4"]

class TestConfigWriterAppendValue(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","name1 =value1","","[section1]","name1= value2"]
    updateLines = ["[DEFAULT]","name2=value3","[section1]","name2=value4"]
    expectedLines = ["[DEFAULT]","name1 = value1","name2 = value3","","[section1]","name1 = value2","name2 = value4"]

class TestConfigWriterAppendSection(ConfigWriterTestCase):
    configLines = ["[DEFAULT]","name1 =value1","","[section1]","name1= value2"]
    updateLines = ["[DEFAULT]","[section2]","name1=value3","name2=value4"]
    expectedLines = ["[DEFAULT]","name1 = value1","","[section1]","name1 = value2","","[section2]","name1 = value3","name2 = value4"]
