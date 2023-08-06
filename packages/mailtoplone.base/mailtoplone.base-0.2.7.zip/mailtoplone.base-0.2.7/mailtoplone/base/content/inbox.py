"""Definition of the InBox content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder

from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from mailtoplone.base import baseMessageFactory as _
from mailtoplone.base.interfaces import IInBox, IMailDropBoxMarker
from mailtoplone.base.config import PROJECTNAME

InBoxSchema = folder.ATFolderSchema.copy() + atapi.Schema((

# Your Archetypes field definitions here ...

))

# Set storage on fields copied from ATFolder, making sure they work
# well with the python bridge properties.

InBoxSchema['title'].storage = atapi.AnnotationStorage()
InBoxSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(InBoxSchema, folderish=True, moveDiscussion=False)

class InBox(folder.ATFolder):
    """A folderish type containing Emails"""
    implements(IInBox, IMailDropBoxMarker)

    portal_type = "InBox"
    _at_rename_after_creation = True
    schema = InBoxSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
atapi.registerType(InBox, PROJECTNAME)
