#!/usr/bin/env python

import unittest
import doctest
import oodoctest

def get_oodoctests():
    common = {'optionflags': doctest.ELLIPSIS}
    EXAMPLES = {
            'examples/example.sxw': {},
            'examples/example.sxw': {'split_level': 2},
            'examples/oodoctest_intro.sxi': {},
            }
    paths = EXAMPLES.keys()

    # Building a suite from multiple paths
    suite = oodoctest.OODocFileSuite(*paths, **common)

    for path, kw in EXAMPLES.items():
        kw.update(common)

        # Building a suite from single path + optional split_level
        suite.addTest(oodoctest.OODocFileSuite(path, **kw))

        # Building a simple test
        suite.addTest(oodoctest.OODocFileTest(path, **common))

    return suite

def run_tests():
    suite = get_oodoctests()
    suite.addTest(doctest.DocTestSuite(oodoctest))
    suite.addTest(doctest.DocFileSuite('README.txt'))
    runner = unittest.TextTestRunner()
    runner.run(suite)

if __name__ == "__main__":
    run_tests()
