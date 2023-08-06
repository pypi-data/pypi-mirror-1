
import os
import unittest

from enthought.setuptools.hierarchical_dict import HierarchicalDict as HDict

class HDictTestCase(unittest.TestCase):

    def test_basic_dict(self):
        d = HDict()
        d["foo"] = 1
        d["bar"] = 3
        d["baz"] = 5
        self.assertEqual(d["foo"], 1)
        self.assertEqual(d["bar"], 3)
        self.assertEqual(d["baz"], 5)

    def test_basic_hierarchy(self):
        for sep in (os.sep, ":", "\\", " > "):
            d = HDict(delimiter=sep)

            nestedkey = sep.join(["foo", "bar", "baz"])
            d[nestedkey] = 42
            self.assertEqual(d[nestedkey], 42)
            self.assertEqual(d["foo"]["bar"]["baz"], 42)

            key2 = sep.join(["foo", "spam"])
            d[key2] = 39
            self.assertEqual(d[key2], 39)
            self.assertEqual(d["foo"]["spam"], 39)
            self.assertEqual(d["foo"]["bar"]["baz"], 42)

            key3 = sep.join(["foo", "bar", "bing"])
            d[key3] = 591
            self.assertEqual(d[key3], 591)
            self.assertEqual(d["foo"]["bar"]["bing"], 591)
            self.assertEqual(d["foo"]["spam"], 39)
            self.assertEqual(d["foo"]["bar"]["baz"], 42)
        return

    def test_unnested(self):
        d = HDict(nested = False)
        key = "foo/bar/baz"
        d[key] = 53
        self.assertEqual(d[key], 53)
        
        d.nested = True
        d.delimiter = "/"
        d[key] = 23
        self.assertEqual(d[key], 23)
        self.assertEqual(d["foo"]["bar"]["baz"], 23)

        d.nested = False
        self.assertEqual(d[key], 53)


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(HDictTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()


