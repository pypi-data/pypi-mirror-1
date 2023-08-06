import sys
import os
import unittest

TOPDIR = os.path.split(os.path.dirname(__file__))[0]
sys.path.insert(0, TOPDIR)

from get_password import Clipboard

class ClipboardTest(unittest.TestCase):

    def test_clip(self):

        cp = Clipboard()
        cp.write('paf')
        self.assertEquals('paf', cp.read())


