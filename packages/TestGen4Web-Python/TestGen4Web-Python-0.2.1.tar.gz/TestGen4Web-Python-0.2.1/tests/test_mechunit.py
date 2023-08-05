import sys
import unittest
from glob import glob
sys.path.extend(['.', '..'])

from testgen.parser import parseXML
from testgen.mechunit import MechanizeUnitTest

from httptestserver import HTTPTestServerMixin

class MechTest(MechanizeUnitTest, HTTPTestServerMixin):
    def setUp(self):
        MechanizeUnitTest.setUp(self)
        self.start_server()

    def tearDown(self):
        MechanizeUnitTest.tearDown(self)
        self.stop_server()

def runSession(sessionFile):
    test = MechTest
    test.sourceFilename = sessionFile
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test)
    suite = unittest.TestSuite(suite)
    unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
    from testgen.mechunit import MechanizeUnitTest
    for sessionFile in glob('sessions/test*.xml'):
        runSession(sessionFile)
