################################################################
# haufe.selenium
#
# (C) 2007, Haufe Mediengruppe
################################################################

"""
Tests
"""

import unittest

class Tests(unittest.TestCase):

    def testSimple(self):
        self.assertEqual(1, 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Tests))
    return suite
