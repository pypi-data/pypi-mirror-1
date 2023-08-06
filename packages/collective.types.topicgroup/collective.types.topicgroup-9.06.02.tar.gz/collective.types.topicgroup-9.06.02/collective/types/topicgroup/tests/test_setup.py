# (C) 2005-2009. University of Washington. All rights reserved.

from unittest import TestSuite
from Products.CMFCore.utils import getToolByName

from collective.types.topicgroup.tests.base import TopicGroupTestCase
from collective.types.topicgroup import TopicGroup
from collective.types.topicgroup.content import ITopicGroup

class TestSetupTypes(TopicGroupTestCase):
    """Make sure we can install types, etc.
    """

    def afterSetUp(self):
        self.types = getToolByName(self.portal, 'portal_types')
        #Create a topicgroup test folder
        self.folder.invokeFactory('Folder', id='test_topicgroup')
        self.folder = self.folder.test_topicgroup

    def testSetup(self):
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        self.assertTrue(qi.isProductInstalled('collective.types.topicgroup'),
                        'collective.types.topicgroup installation failed')
        
    def test_types_versioned(self):
        """Make sure the types are versioned.
        """
        repository = getToolByName(self.portal,
                                   'portal_repository')
        versionable = repository.getVersionableContentTypes()
        self.failUnless('collective.types.TopicGroup' in versionable,
                        'collective.types.TopicGroup is not versionable')

    def test_citation_installed(self):
        self.failUnless('collective.types.TopicGroup' in
                        self.types.objectIds(),
                        'The collective.types.TopicGroup type is not installed')


def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSetupTypes))

    return suite

