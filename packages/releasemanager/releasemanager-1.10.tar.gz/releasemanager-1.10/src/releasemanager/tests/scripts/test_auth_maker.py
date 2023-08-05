"""
tests auth maker and the default anonymous auth class
"""

import os
import unittest
import doctest

def test_auth_maker():
    doc_path = "..%s..%sdocs%stest_auth_maker.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_auth_maker()
