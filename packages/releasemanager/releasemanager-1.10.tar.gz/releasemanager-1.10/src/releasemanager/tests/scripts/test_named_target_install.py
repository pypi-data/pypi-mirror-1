"""
tests named target's install method
"""

import os
import unittest
import doctest

def test_named_target_install():
    doc_path = "..%s..%sdocs%stest_named_target_install.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_named_target_install()
