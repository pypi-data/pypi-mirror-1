"""
tests build host's build method
"""

import os
import unittest
import doctest

def test_build_host_build():
    doc_path = "..%s..%sdocs%stest_build_host_build.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_build_host_build()
