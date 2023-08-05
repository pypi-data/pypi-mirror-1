"""
tests release installer's config reloading and report methods
"""

import os
import unittest
import doctest

def test_release_installer_config_and_report():
    doc_path = "..%s..%sdocs%stest_release_installer_config_and_report.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_release_installer_config_and_report()
