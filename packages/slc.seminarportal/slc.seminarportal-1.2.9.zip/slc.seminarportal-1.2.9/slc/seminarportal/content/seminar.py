from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.event import ATEventSchema

from slc.seminarportal.interfaces import ISeminar
from slc.seminarportal.config import PROJECTNAME, ALLOWABLE_TEXT_TYPES

SeminarSchema = atapi.OrderedBaseFolderSchema.copy() + ATEventSchema.copy() + atapi.Schema((
    atapi.ImageField(
        name='logo',
        widget=atapi.ImageWidget(
            label=u"Graphic or Logo for the event",
            label_msgid='slc.seminar_label_logo',
            i18n_domain='slc.seminar',
        ),
        original_size=(200,200),
        sizes={'thumb': (100, 125), 'normal': (200, 200)},
        default_output_type='image/jpeg',
        allowable_content_types=('image/gif','image/jpeg','image/png'),
    ),
    atapi.TextField(
        name='summary',
        allowable_content_types=ALLOWABLE_TEXT_TYPES,
        widget=atapi.RichWidget(
            label=u"General Description/Summary of the event",
            label_msgid='slc.seminar_label_summary',
            i18n_domain='slc.seminar',
            macro='seminar_textarea',
        ),
        default_output_type="text/x-html-safe",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
    ),
    atapi.TextField(
        name='conclusions',
        allowable_content_types=ALLOWABLE_TEXT_TYPES,
        widget=atapi.RichWidget(
            label=u"General Conclusions",
            label_msgid='slc.seminar_label_conclusions',
            i18n_domain='slc.seminar',
            macro='seminar_textarea',
        ),
        default_output_type="text/x-html-safe",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
    ),
    atapi.TextField(
        name='furtherActions',
        allowable_content_types=ALLOWABLE_TEXT_TYPES,
        widget=atapi.RichWidget(
            label=u"Further Actions",
            label_msgid='slc.seminar_label_further_actions',
            i18n_domain='slc.seminar',
            macro='seminar_textarea',
        ),
        default_output_type="text/x-html-safe",
        searchable=True,
        validators=('isTidyHtmlWithCleanup',),
    ),
    atapi.BooleanField(
        name='showRosterHour',
        widget=atapi.BooleanWidget(
            label=u"Show the hour column in the speech roster?",
            label_msgid='slc.seminar_label_show_hour_column',
            i18n_domain='slc.seminar',
        ),
    ),
))

del SeminarSchema['text']

# Change labels and descriptions
SeminarSchema['description'].widget.label = 'Abstract'
SeminarSchema['description'].widget.description = \
    'A short abstract, introduction or description of the event'

SeminarSchema['contactName'].schemata = 'Organiser'
SeminarSchema['contactName'].widget.label= 'Event Organiser'
SeminarSchema['contactName'].widget.description = \
        "Please provide the name of the event organiser."

SeminarSchema['contactEmail'].schemata = 'Organiser'
SeminarSchema['contactPhone'].schemata = 'Organiser'

SeminarSchema['eventUrl'].schemata = 'Organiser'
SeminarSchema['eventUrl'].widget.label = 'Organiser/Event Website'
SeminarSchema.moveField('eventUrl', after='contactName')

SeminarSchema['location'].widget = atapi.TextAreaWidget(label='Location')
SeminarSchema['location'].searchable = True

schemata.finalizeATCTSchema(SeminarSchema)

# finalizeATCTSchema moves 'location' into 'categories', we move it back:
SeminarSchema.changeSchemataForField('location', 'default')
SeminarSchema.moveField('location', after='description')
SeminarSchema['startDate'].widget.format = '%A %d %B %Y %H:%M'
SeminarSchema['endDate'].widget.format = '%A %d %B %Y %H:%M'

class SPSeminar(atapi.OrderedBaseFolder, ATEvent):
    """Description of the Example Type"""
    implements(ISeminar)
    meta_type = portal_type = "SPSeminar"
    schema = SeminarSchema

    _at_rename_after_creation = True

    def seminar_title(self):
        return self.Title()

    def get_path(self):
        return '/'.join(self.getPhysicalPath()) 

    def get_seminar_start_date(self):
        return self.startDate

    def get_seminar_end_date(self):
        return self.endDate
         
atapi.registerType(SPSeminar, PROJECTNAME)


