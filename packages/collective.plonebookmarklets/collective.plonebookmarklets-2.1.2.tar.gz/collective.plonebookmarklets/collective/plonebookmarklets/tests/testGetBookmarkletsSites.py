from Products.CMFPlone.tests import PloneTestCase
from unittest import TestSuite, makeSuite
from Testing import ZopeTestCase
from Testing.ZopeTestCase import user_name
from AccessControl import Unauthorized
from base import PloneBookmarkletsTestCase
from collective.plonebookmarklets.interfaces import IPloneBookmarkletsLayer
from Products.Five import zcml
import collective.plonebookmarklets
from collective.plonebookmarklets.browser import BookmarkletsView


class testGetBookmarkletsSites(PloneBookmarkletsTestCase):


    def test_get_sites(self):
        self.setRoles(['Manager',])
        folder = getattr(self.portal,self.portal.invokeFactory('Folder','test-folder'),None)        
        self.setRoles(['Member',])

        view = BookmarkletsView(folder,self.app.REQUEST)
        portal_props = self.portal.portal_properties
        bm_props = portal_props.bookmarklets_properties
        assert len(view.getSites()) == len(bm_props.getProperty('available_sites')), "PloneBookmarklets, getSites() failed"


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(testGetBookmarkletsSites))
    suite.layer = IPloneBookmarkletsLayer
    return suite

