"""Tests for methods that ask WC for realm-level or user-related data.
"""

import unittest
from PyWhatCounts.Wrapper import WCWrapper
from PyWhatCounts.exceptions import WCUserError, WCSystemError, WCAuthError
# this is the config here locally in the tests dir
from config import TEST_REALM, TEST_KEY, TEST_DUMMY_USER, TEST_LIST

class testShowLists(unittest.TestCase):
    """
    Show lists should be pretty bomber; it just takes a realm and pwd.
    """
    def setUp(self):
        self.pwc = WCWrapper()
        self.pwc._setConnectionInfo(TEST_REALM, TEST_KEY)

    def testShowLists(self):
        """Make sure that the TEST_LIST is among the results of the realm's lists"""
        # It would be far more thorough if it compared results with the actual
        # lists and names in this realm, but that would be a little hard to maintain

        # note that the list id is the first of each pair returned by the method;
        # the name is the second value
        list_ids = [l[0] for l in self.pwc.showLists()]
        self.failUnless(TEST_LIST in list_ids)

    def testFailsWithBadCreds(self):
        """Make sure we raise an exception with bad user name/pass"""
        # It would be far more thorough if it compared results with the actual
        # lists and names in this realm, but that would be a little hard to maintain

        # note that the list id is the first of each pair returned by the method;
        # the name is the second value
        # bad pwd
        self.pwc._setConnectionInfo(TEST_REALM, '123')
        self.assertRaises(WCAuthError, self.pwc.showLists)
        # bad realm
        self.pwc._setConnectionInfo('whatcounts', TEST_KEY)
        self.assertRaises(WCAuthError, self.pwc.showLists)


class testGetUserDetails(unittest.TestCase):
    """
    
    """
    def setUp(self):
        self.pwc = WCWrapper()
        self.pwc._setConnectionInfo(TEST_REALM, TEST_KEY)
        self.pwc.subscribeUser(TEST_DUMMY_USER, TEST_LIST)



    def testGetsDetails(self):
        """Basic func test"""
        dummy = self.pwc.getUserDetails(TEST_DUMMY_USER)
        self.failUnless(dummy['email']==TEST_DUMMY_USER)
        
    def testBonksOnNonExistantUser(self):
        """If the user doesn't exist, raise a WCUserError"""
        self.assertRaises(WCUserError, self.pwc.getUserDetails, 'bogus@onenw.org')


    def tearDown(self):
        self.pwc._deleteUser(TEST_DUMMY_USER)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testShowLists))
    suite.addTest(makeSuite(testGetUserDetails))
    return suite

             
if __name__ == '__main__':
    unittest.main()