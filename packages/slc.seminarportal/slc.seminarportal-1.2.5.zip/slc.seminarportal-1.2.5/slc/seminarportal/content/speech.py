from zope.interface import implements

from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.event import ATEventSchema
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.Archetypes import atapi
from Products.Relations.field import RelationField

from slc.seminarportal import seminarportalMessageFactory as _
from slc.seminarportal.config import PROJECTNAME
from slc.seminarportal.interfaces import ISpeech
from slc.seminarportal.permissions import ASSIGN_SPEECHES_TO_SPEAKERS

SpeechSchema = atapi.OrderedBaseFolderSchema.copy() + ATEventSchema.copy() + atapi.Schema((
    RelationField(
        name='speakers',
        widget=ReferenceBrowserWidget(
            label=u'Speakers',
            label_msgid='slc.seminarportal_label_speakers',
            i18n_domain='slc.seminarportal',
            base_query={'portal_type':'SPSpeaker', 'sort_on':'getSortableName'},
            allow_browse=1,
            allow_search=1,
            show_results_without_query=1,            
            image_portal_types=('SPSpeaker',),
            image_method='user.gif',
        ),
        write_permission=ASSIGN_SPEECHES_TO_SPEAKERS,
        allowed_types=('SPSpeaker',),
        multiValued=1,
        relationship='speech_speakers',
    ),
))

SpeechSchema['description'].widget.label = 'Abstract'
SpeechSchema['description'].widget.description = \
    'A short abstract, introduction or description of the speech'
SpeechSchema['text'].widget.label = \
    _(u'label_event_announcement', default=u'Conclusions')
SpeechSchema['location'].widget.label = \
    _(u'label_event_location', default=u'Location')
SpeechSchema['startDate'].widget.format = '%A %d %B %Y %H:%M'
SpeechSchema['endDate'].widget.format = '%A %d %B %Y %H:%M'

class SPSpeech(atapi.BaseFolder, ATEvent):
    """ Represents a Speech held during a seminar. 
    """ 
    implements(ISpeech)

    meta_type = portal_type = "SPSpeech"
    schema = SpeechSchema

    _at_rename_after_creation = True

    def get_path(self):
        return '/'.join(self.getPhysicalPath()) 

atapi.registerType(SPSpeech, PROJECTNAME)

