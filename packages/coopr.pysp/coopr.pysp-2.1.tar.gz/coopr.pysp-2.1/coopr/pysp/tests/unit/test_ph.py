#
# Get the directory where this script is defined, and where the baseline
# files are located.
#
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep
#
# Import the testing packages
#
import unittest
import pyutilib.misc
import pyutilib.th

#
# Define a testing class, using the pyutilib.th.TestCase class.  This is
# an extension of the unittest.TestCase class that adds additional testing
# functions.
#
class TestPH(pyutilib.th.TestCase):

    #
    # A test which redirects IO to a file, prints stuff, resets the
    # redirection, and then compares with a baseline file.
    #
    def test_dummy(self):
        pyutilib.misc.setup_redirect(currdir+"dummy.out")
        print "HELLO WORLD"
        pyutilib.misc.reset_redirect()
        self.failUnlessFileEqualsBaseline(currdir+"dummy.out",currdir+"dummy.txt")

if __name__ == "__main__":
   unittest.main()
