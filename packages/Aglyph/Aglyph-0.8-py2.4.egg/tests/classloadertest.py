import httplib
import unittest

import aglyph.classloader
import aglyph.definition

import tests


class ClassLoaderTest(unittest.TestCase):

    def test_load_class(self):
        cl = aglyph.classloader.ClassLoader()
        self.assertEqual(cl.load_class("__builtin__.int"), int,
            "failed to load __builtin__.int")
        self.assertEqual(cl.load_class("httplib.HTTPConnection"),
            httplib.HTTPConnection, "failed to load httplib.HTTPConnection")
        self.assertEqual(
            cl.load_class("tests.Thing"),
            tests.Thing,
            "failed to load tests.Thing")
        self.assertEqual(cl.load_class("aglyph.definition.Value"),
            aglyph.definition.Value, "failed to load aglyph.definition.Value")
        self.assertEqual(cl.load_class("aglyph.definition.NamedValue"),
            aglyph.definition.NamedValue,
            "failed to load aglyph.definition.NamedValue")
        self.assertEqual(cl.load_class("aglyph.definition.Setter"),
            aglyph.definition.Setter,
            "failed to load aglyph.definition.Setter")
        self.assertEqual(cl.load_class("aglyph.definition.Reference"),
            aglyph.definition.Reference,
            "failed to load aglyph.definition.Reference")


if (__name__ == "__main__"):
    unittest.main()

