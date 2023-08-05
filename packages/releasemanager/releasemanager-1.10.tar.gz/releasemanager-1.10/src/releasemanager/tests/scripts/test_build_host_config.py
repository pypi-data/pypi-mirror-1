"""
tests build host's ability to reload its own config
"""

import os
import unittest
import doctest

def test_build_host_config():
    doc_path = "..%s..%sdocs%stest_build_host_config.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_build_host_config()
