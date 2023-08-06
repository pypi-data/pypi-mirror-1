"""Definition of the Topic Group content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.CMFPlone import PloneMessageFactory as _

from collective.types.topicgroup.config import PROJECTNAME

from zope.interface import Interface

from Products.CMFPlone import PloneMessageFactory as _

class ITopicGroup(Interface):
    """Specialized ATFolder to display contents in a grouped fashion"""
TopicGroupSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

TopicGroupSchema['title'].storage = atapi.AnnotationStorage()
TopicGroupSchema['description'].storage = atapi.AnnotationStorage()

# hide from navigation
TopicGroupSchema['excludeFromNav'].default = True

schemata.finalizeATCTSchema(TopicGroupSchema, folderish=True, moveDiscussion=False)

class TopicGroup(folder.ATFolder):
    """Specialized ATFolder to display contents in a grouped fashion"""
    implements(ITopicGroup)

    portal_type = meta_type = "collective.types.TopicGroup"
    schema = TopicGroupSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # Specialized to hide the Display menu (otherwise, even with only one
    # view available, "Select a content item as default view..." shows up).
    def canSetDefaultPage(self):
        return False

atapi.registerType(TopicGroup, PROJECTNAME)
