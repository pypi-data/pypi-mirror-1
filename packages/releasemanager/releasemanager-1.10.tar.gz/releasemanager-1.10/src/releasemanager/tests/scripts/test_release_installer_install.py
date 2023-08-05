"""
tests release installer's install method
"""

import os
import unittest
import doctest

def test_release_installer_install():
    doc_path = "..%s..%sdocs%stest_release_installer_install.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_release_installer_install()
