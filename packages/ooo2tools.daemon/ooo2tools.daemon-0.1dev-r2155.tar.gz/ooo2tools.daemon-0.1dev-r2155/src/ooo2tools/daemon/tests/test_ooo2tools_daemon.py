import doctest
import unittest

class TestOO2(unittest.TestCase):

    def setUp(self):
        print "pre"
 
    def test1(self):
        self.assertEquals(1, 1)

    def tearDown(self):
        print "post"

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestOO2))
    return suite


