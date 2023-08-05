"""
tests basic auth
"""

__docformat__ = "reStructuredText"

import os, sys
import unittest
import doctest

def test_basic_auth():
    doc_path = "..%sdocs%sbasic_auth.txt" % (os.sep, os.sep)
    suite = doctest.DocFileSuite(doc_path)
    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    test_basic_auth()
