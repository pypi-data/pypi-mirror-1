"""
Run 'make tests' or just 'make' at parent directory. Thanks.
"""

import os
import glob
import unittest
import doctest

if __name__ == "__main__":
    suite = unittest.TestSuite()

    filematch = os.path.join(os.path.dirname(__file__), "*.test")
    for test in glob.glob(filematch):
        test = os.path.split(test)[1]
        suite.addTest(doctest.DocFileSuite(test))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
