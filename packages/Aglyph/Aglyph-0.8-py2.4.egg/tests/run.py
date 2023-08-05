import unittest

from tests.assemblertest import AssemblerTest
from tests.cachetest import CacheTest
from tests.classloadertest import ClassLoaderTest
from tests.contexttest import XmlContextTest
from tests.definitiontest import EvaluatorTest
from tests.definitiontest import DefinitionTest


def loadTestSuite():
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    suite.addTest(loader.loadTestsFromTestCase(AssemblerTest))
    suite.addTest(loader.loadTestsFromTestCase(CacheTest))
    suite.addTest(loader.loadTestsFromTestCase(ClassLoaderTest))
    suite.addTest(loader.loadTestsFromTestCase(XmlContextTest))
    suite.addTest(loader.loadTestsFromTestCase(EvaluatorTest))
    suite.addTest(loader.loadTestsFromTestCase(DefinitionTest))
    return suite


if (__name__ == "__main__"):
    unittest.TextTestRunner(verbosity=2).run(loadTestSuite())

