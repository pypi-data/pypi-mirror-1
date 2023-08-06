"""Tests for our private helper methods.
"""

import unittest
from PyWhatCounts.Wrapper import WCWrapper
from PyWhatCounts.exceptions import WCUserError, WCSystemError, WCAuthError
# this is the config here locally in the tests dir
from config import TEST_REALM, TEST_KEY, TEST_DUMMY_USER, TEST_LIST

class testFindUser(unittest.TestCase):
    """
    """
    def setUp(self):
        self.pwc = WCWrapper()
        self.pwc._setConnectionInfo(TEST_REALM, TEST_KEY)
        self.pwc.subscribeUser(TEST_DUMMY_USER, TEST_LIST)


    def testActuallyFindsUser(self):
        # this is just the basic test that we're returning the correct data
        self.failUnless(self.pwc._findUser(TEST_DUMMY_USER)['email'] == TEST_DUMMY_USER)

    def testBonksOnNonExistantUser(self):
        """Raise a WCUserError if user doesn't exist in realm"""
        self.assertRaises(WCUserError, self.pwc._findUser, 'foo@bar.com')


    def tearDown(self):
        self.pwc._deleteUser(TEST_DUMMY_USER)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testFindUser))
    return suite

             
if __name__ == '__main__':
    unittest.main()