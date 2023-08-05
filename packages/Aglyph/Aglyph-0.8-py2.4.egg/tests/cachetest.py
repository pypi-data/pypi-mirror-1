import time
import unittest

import aglyph.cache


class CacheTest(unittest.TestCase):

    def test_cache_access(self):
        # Test a cache whose entries never expire (i.e. behavior is identical
        # to using a regular dictionary for a cache)
        never = aglyph.cache.Cache(aglyph.cache.Cache.NEVER_EXPIRE)
        never["key"] = "value"
        self.assertEqual(never.get("key"), "value",
            "never.get('key') != 'value' before sleep")
        time.sleep(1)
        self.assertEqual(never.get("key"), "value",
            "never.get('key') != 'value' after sleep")
        del never["key"]
        self.assertEqual(never.get("key"), None,
            "never.get('key') != None after __delitem__")
        # Test a cache whose entries always expire (this means that __getitem__
        # and __delitem__ ALWAYS raise KeyError)
        always = aglyph.cache.Cache(aglyph.cache.Cache.ALWAYS_EXPIRE)
        always["key"] = "value"
        self.failUnlessRaises(KeyError, always.__getitem__, "key")
        self.assertEqual(always.get("key"), None, "always.get('key') != None")
        # Test a cache whose entries expire after two seconds
        twosecs = aglyph.cache.Cache(2)
        twosecs["key"] = "value"
        self.assertEqual(twosecs.get("key"), "value",
            "twosecs.get('key') != 'value' before sleep")
        time.sleep(2.1)
        self.assertEqual(twosecs.get("key"), None,
            "twosecs.get('key') != None after sleep")


if (__name__ == "__main__"):
    unittest.main()

