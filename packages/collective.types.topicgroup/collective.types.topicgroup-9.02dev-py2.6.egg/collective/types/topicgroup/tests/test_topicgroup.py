# (C) 2005-2009. University of Washington. All rights reserved.

from unittest import TestSuite

from collective.types.topicgroup.tests.base import TopicGroupTestCase
from collective.types.topicgroup.tests.base import Session
from collective.types.topicgroup import TopicGroup
from collective.types.topicgroup.content import ITopicGroup

class TestCreateTopicGroup(TopicGroupTestCase):
    """Make sure we can create TopicGroups 
    """

    def testCreateTopicGroup(self):
        self.folder.invokeFactory('collective.types.TopicGroup',
                                  id='tg1')
        tg = self.folder.tg1
        self.assertEquals('tg1', tg.id,
                          "TopicGroup id should be 'tg1' "\
                          ", instead it's %s" % \
                          tg.id)
        self.assertEquals(tg.default_view, 'base_view',
                          'default_view should be base_view')

def test_suite():
    from unittest import TestSuite
    from unittest import makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestCreateTopicGroup))

    return suite

