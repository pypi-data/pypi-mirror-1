# -*- coding: utf-8 -*-

__author__ = """WebLion <support@weblion.psu.edu>"""
__docformat__ = 'plaintext'

#
# Test-cases for AnonymousCommenting
#

from Products.CMFCore.utils import getToolByName
import Products.AnonymousCommenting
from Products.AnonymousCommenting.tests.base import AnonymousCommentingTestCase

class testAnonymousCommenting(AnonymousCommentingTestCase):

    def test_anonymousCommentingEnabled(self):
        self.failUnless('Anonymous' in self.portal._Reply_to_item_Permission, "The Anonymous role does not have the 'Reply to item' permission.")

    def test_nameOnForm(self):
        self.failUnless('value="test_user_1_"' in self.portal['front-page']['discussion_reply_form'](), "The logged in user's name was not included in the comment form's name field.")
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testAnonymousCommenting))
    return suite