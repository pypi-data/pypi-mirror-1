"""
tests release builder's build method
"""

import os
import unittest
import doctest

def test_release_builder_build():
    doc_path = "..%s..%sdocs%stest_release_builder_build.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_release_builder_build()
