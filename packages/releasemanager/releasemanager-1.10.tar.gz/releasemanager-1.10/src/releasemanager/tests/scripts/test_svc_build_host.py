"""
tests the service oriented build host's build method
caveat is that a template builder service must be running
at localhost:9999.  i don't know enough about mocking services
to try to meaningfully set up a test scenario for twisted xmlrpc
"""

import os
import unittest
import doctest

def test_svc_build_host():
    doc_path = "..%s..%sdocs%stest_svc_build_host.txt" % (os.sep, os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_svc_build_host()
