"""Definition of the SPSpeakersFolder content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from slc.seminarportal import seminarportalMessageFactory as _
from slc.seminarportal.interfaces import ISpeakersFolder
from slc.seminarportal.config import PROJECTNAME

SPSpeakersFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

SPSpeakersFolderSchema['title'].storage = atapi.AnnotationStorage()
SPSpeakersFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(SPSpeakersFolderSchema, folderish=True, moveDiscussion=False)

class SPSpeakersFolder(folder.ATFolder):
    """Folder containing Seminar Speakers"""
    implements(ISpeakersFolder)

    portal_type = "SPSpeakersFolder"
    schema = SPSpeakersFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

atapi.registerType(SPSpeakersFolder, PROJECTNAME)
